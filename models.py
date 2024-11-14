from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.db.models.signals import post_save

class Profile(models.Model):
    USER_ROLES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('installer', 'Installer'),
        ('electricity_provider', 'Electricity Provider'),
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
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),  # Money credited to provider (from customer)
        ('debit', 'Debit'),    # Money debited from provider (e.g., refunds or adjustments)
    ]
    
    provider_profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_role': 'electricity_provider'},
        related_name='transactions'
    )
    customer_profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_role': 'customer'},
        related_name='customer_transactions',
        blank=True, 
        null=True
    )
    energy_purchased = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Energy purchased in kWh, applicable for completed transactions."
    )
    total_payment = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Total payment amount for the transaction."
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.provider_profile.user.username} - {self.transaction_type} - {self.amount}"

    class Meta:
        ordering = ['-date']  # Order transactions by date, most recent first

class Bid(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('withdrawn', 'Withdrawn'),
        ('expired', 'Expired'),
    ]

    customer_profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_role': 'customer'}, 
        related_name='customer_bids'
    )
    provider_profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_role': 'electricity_provider'}, 
        related_name='provider_bids'
    )
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_profile.user.username} - {self.bid_amount}"

class RateSetting(models.Model):
    provider_profile = models.OneToOneField(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'electricity_provider'})
    current_buyback_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    new_buyback_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    effective_date = models.DateField(blank=True, null=True)

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

class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, null=True)  # New field for brand name
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)  # New field for image
    vendor_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'vendor'}, null=False)
    panel_size = models.FloatField(default=0.0)  # Add this field to compare against estimated size
    
    def __str__(self):
        return f"{self.brand} - {self.name}"

class CartItem(models.Model):
    customer_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'customer'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Ensure quantity is a positive integer
        if self.quantity <= 0:
            raise ValidationError('Quantity must be greater than zero.')

    def save(self, *args, **kwargs):
        # Remove the logic for price_at_addition since it's no longer in the model
        # You can use the product price directly in the view or template
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart Item: {self.product.name} for {self.customer_profile.user.username}"

    def total_price(self):
        # You can calculate the total price of this cart item using the current product price
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
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

    def __str__(self):
        return f"Order by {self.customer_profile.user.username} - {self.product.name}"

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

class InstallerService(models.Model):
    installer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='installation_services')
    service_name = models.CharField(max_length=255)
    description = models.TextField()
    panel_size_range_min = models.FloatField(help_text="Minimum size of solar panels (in kW) for this service")
    panel_size_range_max = models.FloatField(help_text="Maximum size of solar panels (in kW) for this service")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this installation service")
    
    # New field added with a default value
    installer_address = models.CharField(max_length=255, default="Unknown", help_text="Address of the installer")
    
    def __str__(self):
        return f"{self.service_name} by {self.installer.user.username}"

    class Meta:
        verbose_name = "Installation Service"
        verbose_name_plural = "Installation Services"

class QuoteRequestInstaller(models.Model):
    customer_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'customer'})
    panel_size_min = models.IntegerField()  # Min solar panel size (kW)
    panel_size_max = models.IntegerField()  # Max solar panel size (kW)
    quote_deadline = models.DateField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')

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

class Quote(models.Model):
    quote_request = models.ForeignKey(QuoteRequestInstaller, on_delete=models.CASCADE)
    installer_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'installer'})
    price_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')

class InstallationBooking(models.Model):
    quote_submission_installer = models.ForeignKey(QuoteSubmissionInstaller, on_delete=models.CASCADE)
    installer = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_role': 'installer'})
    customer_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='customer_installations',
        limit_choices_to={'user_role': 'customer'}, null=True, blank=True
    )
    solar_panel_size = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    installation_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('booked', 'Booked'), ('completed', 'Completed')], default='pending')

    def __str__(self):
        # Safely handle None for customer_profile, installer, and quote_submission_installer
        customer_name = "Unknown Customer"
        if self.customer_profile and self.customer_profile.user:
            customer_name = self.customer_profile.user.username  # Accessing the username of the customer
        
        installer_name = "Unknown Installer"
        if self.installer:
            installer_name = self.installer.user.username if self.installer.user else "Unknown Installer"  # Accessing the username of the installer
        
        quote_id = "No Quote ID"
        if self.quote_submission_installer:
            quote_id = self.quote_submission_installer.id  # Using quote submission ID
        
        # Returning a formatted string with customer username, installer username, and quote ID
        return f"Installation for {customer_name} by Installer {installer_name} (Quote ID {quote_id})"




