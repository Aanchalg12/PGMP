from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.db.models.signals import post_save
from decimal import Decimal

class Profile(models.Model):
    USER_ROLES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('installer', 'Installer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    user_role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    company_name = models.CharField(max_length=100, blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)
    certificate_no = models.CharField(max_length=50, blank=True, null=True)
    provider_license = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default_profile.jpg')
    city = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def clean(self):
        if not self.user:
            raise ValidationError("User is required for the profile.")

class Installation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('incomplete', 'Incomplete'),
        ('completed', 'Completed'),
    ]
    
    # Directly linking to Profile model, so the `customer` field can refer to users with customer roles
    customer_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'customer'})
    address = models.CharField(max_length=255)
    solar_panel_size = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.customer_profile.user.username} - {self.solar_panel_size}"
    
class Product(models.Model):
    # General product details
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Base price (panel only)
    stock_quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    vendor_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, 
        limit_choices_to={'user_role': 'vendor'}, null=False
    )

    # Solar panel-specific details
    panel_size = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'))  # kW

    # Battery-specific details
    has_battery = models.BooleanField(default=True)
    battery_capacity = models.DecimalField(
        max_digits=6, decimal_places=2, 
        null=True, blank=True, 
        help_text="Battery capacity in kWh"
    )
    battery_type = models.CharField(
        max_length=50, 
        null=True, blank=True, 
        choices=[('Li-ion', 'Lithium-Ion'), ('Lead-Acid', 'Lead Acid')],
        help_text="Type of battery"
    )
    battery_cost = models.DecimalField(
        max_digits=10, decimal_places=2, 
        null=True, blank=True, 
        help_text="Cost of the battery"
    )

    def get_dynamic_price(self, panel_size):
        # Calculate dynamic price based on panel size
        panel_size = Decimal(panel_size)
        price_multiplier = Decimal('1.5')  # Hypothetical growth rate
        base_price = self.price * (price_multiplier ** (panel_size - 1))

        # Add battery cost if a battery is included
        #if self.has_battery and self.battery_cost:
        #   return base_price + self.battery_cost
        return base_price

    def clean(self):
        # Validation logic
        if self.panel_size <= 0:
            raise ValidationError("Panel size must be greater than zero.")
        if self.price <= 0:
            raise ValidationError("Price must be greater than zero.")
        if self.has_battery:
            if not self.battery_capacity or not self.battery_type or not self.battery_cost:
                raise ValidationError("Battery capacity, type, and cost must be specified if the product includes a battery.")
            if self.battery_cost <= 0:
                raise ValidationError("Battery cost must be greater than zero.")

    def save(self, *args, **kwargs):
        # Clean and validate before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} - {self.name} {'(with Battery)' if self.has_battery else ''}"
    
class CartItem(models.Model):
    customer_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'customer'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Store price when added to cart

    def clean(self):
        # Ensure quantity is a positive integer
        if self.quantity <= 0:
            raise ValidationError('Quantity must be greater than zero.')

    def save(self, *args, **kwargs):
        # Set price_at_addition dynamically when the CartItem is first created
        if not self.price_at_addition:  # Only set it once when the item is first added
            self.price_at_addition = self.product.get_dynamic_price(self.product.panel_size)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart Item: {self.product.name} for {self.customer_profile.user.username}"

    def total_price(self):
        # Calculate the total price using the dynamic price at the time the item was added
        return self.price_at_addition * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Customer Profile
    customer_profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_role': 'customer'}, 
        related_name='customer_orders',
        null=True
    )
    
    # Vendor Profile
    vendor_profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_role': 'vendor'}, 
        related_name='vendor_orders' 
    )

    # Product Details
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date = models.DateField(default=date.today)

    def clean(self):
        """
        Ensure that sufficient stock is available before saving the order.
        """
        if self._state.adding and self.product and self.quantity > self.product.stock_quantity:
            raise ValidationError(f"Not enough stock for {self.product.name}. Available: {self.product.stock_quantity}")

    def save(self, *args, **kwargs):
        """
        Handle stock reduction when an order is created and restock when canceled.
        """
        if self._state.adding:  # New Order
            if self.product.stock_quantity >= self.quantity:
                self.product.stock_quantity -= self.quantity
                self.product.save()
            else:
                raise ValidationError(f"Insufficient stock for {self.product.name}.")
        else:
            # Handle cancellation scenario
            previous = Order.objects.get(pk=self.pk)
            if previous.status != 'cancelled' and self.status == 'cancelled':
                self.product.stock_quantity += previous.quantity
                self.product.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order by {self.customer_profile.user.username} - {self.product.name} ({self.quantity})"

class QuoteRequest(models.Model):
    customer_profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_role': 'customer'},
        related_name='customer_quotes'
    )
    vendor = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        null=True, 
        limit_choices_to={'user_role': 'vendor'},
        related_name='vendor_requests'  # Unique related_name for the vendor field
    )
    estimation_details = models.TextField()
    quote_deadline = models.DateField()
    status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], 
        default='pending'
    )
    submitted = models.BooleanField(default=False)

    def __str__(self):
        vendor_username = self.vendor.user.username if self.vendor else "No vendor"
        customer_username = self.customer_profile.user.username if self.customer_profile else "No customer"
        return f"Quote for {customer_username} to {vendor_username}"

class QuoteSubmission(models.Model):
    quote_request = models.ForeignKey(QuoteRequest, on_delete=models.CASCADE)
    
    # Vendor for solar panel quotes
    vendor = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'vendor'}, related_name='vendor_quotes')
    
    # Installer for installation quotes
    installer = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'installer'}, related_name='installer_quotes', null=True, blank=True)
    
    price_estimate = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(
        max_length=10, 
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')],
        default='pending'
    )  # Add status field to track the quote's state

    def __str__(self):
        if self.vendor:
            return f"Vendor submission for {self.quote_request.id}"
        elif self.installer:
            return f"Installer submission for {self.quote_request.id}"
        return f"Submission for {self.quote_request.id}"

class SolarEstimation(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='estimations')  
    postcode = models.CharField(max_length=10)
    longitude = models.FloatField()
    latitude = models.FloatField()
    electricity_bill = models.DecimalField(max_digits=10, decimal_places=2)
    house_type = models.CharField(max_length=50)
    solar_irradiance = models.FloatField()
    estimated_size_kw = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    annual_savings = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payback_period = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Solar Estimation for {self.user.user.username}"  

class QuoteRequestInstaller(models.Model):
    customer_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'customer'})
    panel_size = models.IntegerField() 
    quote_deadline = models.DateField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    submitted = models.BooleanField(default=False)

class QuoteSubmissionInstaller(models.Model):
    quote_request_installer = models.ForeignKey(QuoteRequestInstaller, on_delete=models.CASCADE)
    installer = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'installer'})
    price_estimate = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')],
        default='pending'
    )

    def __str__(self):
        return f"Installer submission for Quote Request ID {self.quote_request_installer.id}"

class InstallerService(models.Model):
    installer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='installation_services')
    service_name = models.CharField(max_length=255)
    description = models.TextField()
    panel_size = models.FloatField(default="1", help_text=" size of solar panels (in kW) for this service")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this installation service")
    
    # New field added with a default value
    installer_address = models.CharField(max_length=255, default="Unknown", help_text="Address of the installer")
    
    # Add a ForeignKey to QuoteSubmissionInstaller to associate the service with quote submissions
    quote_submission_installer = models.ForeignKey(
        QuoteSubmissionInstaller, 
        on_delete=models.CASCADE, 
        related_name='installer_services',
        blank=True, null=True  # Allowing null values, in case not all services have a quote submission
    )
    
    def __str__(self):
        return f"{self.service_name} by {self.installer.user.username}"

    class Meta:
        verbose_name = "Installation Service"
        verbose_name_plural = "Installation Services"

class Installer(models.Model):
    company_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    city = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=10, default='0000')
    license_number = models.CharField(max_length=100, blank=True, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='installers')  # Added related_name here
    installerservice = models.CharField(max_length=255, default="Default Service")
    
    def __str__(self):
        return self.company_name

class Quote(models.Model):
    quote_request = models.ForeignKey(QuoteRequestInstaller, on_delete=models.CASCADE)
    installer_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'installer'})
    price_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    submitted = models.BooleanField(default=False)

class InstallationBooking(models.Model):
    quote_submission_installer = models.ForeignKey(QuoteSubmissionInstaller, on_delete=models.CASCADE, null=True, blank=True)
    installer = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'installer'})
    customer_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='customer_installations',
        limit_choices_to={'user_role': 'customer'}, null=True, blank=True
    )
    solar_panel_size = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    installation_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('booked', 'Booked'), ('completed', 'Completed')], default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_per_kw = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1200.00')) 
    
    def calculate_total_price(self):
        #price_per_kw = Decimal('1000.00')  # Example price per kW (adjust based on your pricing structure)
        price_per_kw_float = Decimal(self.price_per_kw)  # Ensure price_per_kw is a Decimal
        return self.solar_panel_size * price_per_kw_float

    def save(self, *args, **kwargs):
        # Calculate total price before saving
        if not self.total_price or self.total_price == Decimal('0.00'):
            self.total_price = self.calculate_total_price()
        
        super().save(*args, **kwargs)

    def __str__(self):
        customer_name = "Unknown Customer"
        if self.customer_profile and self.customer_profile.user:
            customer_name = self.customer_profile.user.username
        
        installer_name = "Unknown Installer"
        if self.installer:
            installer_name = self.installer.user.username if self.installer.user else "Unknown Installer"
        
        quote_id = "No Quote ID"
        if self.quote_submission_installer:
            quote_id = self.quote_submission_installer.id
        
        return f"Installation for {customer_name} by Installer {installer_name} (Quote ID {quote_id})"

class PostcodeRegion(models.Model):
    postcode_prefix = models.CharField(max_length=5, unique=True)  # e.g., 'AB', 'AL', 'B'
    region = models.CharField(max_length=100)  # Region like 'Scotland', 'East of England'

    def __str__(self):
        return f"{self.postcode_prefix} - {self.region}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating scale from 1 to 5
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"

class InstallerReview(models.Model):
    installer = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="reviews",
        limit_choices_to={'user_role': 'installer'},  # Only allow reviews for installers
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The reviewer
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating scale from 1 to 5
    review_text = models.TextField(blank=True)  # Optional textual review
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.installer.user.username}"

    class Meta:
        unique_together = ('installer', 'user')