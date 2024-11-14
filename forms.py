
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .validators import validate_uk_postcode
from .models import Profile, Product, CartItem, QuoteRequest, QuoteSubmission, InstallerService, QuoteRequestInstaller, Quote, QuoteSubmissionInstaller
from django.core.exceptions import ValidationError
from django.db import models


class SignupForm(UserCreationForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

#add user
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    mobile = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    user_role = forms.ChoiceField(choices=[
        ('installer', 'Installer/Maintenance'),
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('electricity_provider', 'Electricity Provider'),
    ], widget=forms.Select(attrs={'class': 'form-control'}))
    company_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'address', 'mobile', 'password', 'user_role', 'company_name']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hash the password
        if commit:
            user.save()

        # Check if the user already has a profile
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'address': self.cleaned_data.get('address'),
                'mobile': self.cleaned_data.get('mobile'),
                'user_role': self.cleaned_data.get('user_role'),
                'company_name': self.cleaned_data.get('company_name', '')
            }
        )

        # If the profile was not created (i.e., it already exists), update the profile
        if not created:
            profile.address = self.cleaned_data.get('address', '')
            profile.mobile = self.cleaned_data.get('mobile', '')
            profile.user_role = self.cleaned_data.get('user_role', '')
            profile.company_name = self.cleaned_data.get('company_name', '')
            profile.save()

        return user
    
class UserEditForm(forms.ModelForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    mobile = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    user_role = forms.ChoiceField(choices=[
        ('installer', 'Installer/Maintenance'),
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('electricity_provider', 'Electricity Provider'),
    ], widget=forms.Select(attrs={'class': 'form-control'}))
    company_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'address', 'mobile', 'password', 'user_role', 'company_name']

    def save(self, commit=True):
        user = super(UserEditForm, self).save(commit=False)
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'mobile', 'user_role', 'company_name']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'mobile', 'company_name', 'user_role', 'profile_picture']  # Added profile_picture
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'user_role': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),  # Added widget for profile picture
        }

class ProfilePhotoChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']  # Make sure this field exists in your Profile model

    # Optional: You can customize the widgets if needed
    def __init__(self, *args, **kwargs):
        super(ProfilePhotoChangeForm, self).__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'brand', 'description', 'price', 'stock_quantity', 'image', 'panel_size']

class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = ['estimation_details', 'quote_deadline']

    def __init__(self, *args, **kwargs):
        # Extract the user and estimation
        self.user = kwargs.pop('user', None)
        self.estimation = kwargs.pop('estimation', None)
        super().__init__(*args, **kwargs)

        # Set initial values for the form fields
        if self.estimation:
            self.fields['estimation_details'].initial = f"Estimated Solar Panel Size: {self.estimation.estimated_size_kw} kW"
            self.fields['quote_deadline'].initial = self.estimation.created_at.date()
        else:
            self.fields['estimation_details'].initial = "No estimation available."
            self.fields['quote_deadline'].initial = None

        # If you want to pre-fill vendor info based on the product's vendor
        if 'vendor' in kwargs:
            self.fields['vendor'].initial = kwargs['vendor']

class QuoteSubmissionForm(forms.ModelForm):
    class Meta:
        model = QuoteSubmission
        fields = ['price_estimate', 'notes']  # Add any other relevant fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price_estimate'].label = "Price Estimate (£)"
        self.fields['notes'].label = "Additional Notes"

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']  # Allow only quantity to be editable

    # You can also add custom validation if needed
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

class InstallationServiceForm(forms.ModelForm):
    class Meta:
        model = InstallerService
        fields = ['service_name', 'description', 'panel_size_range_min', 'panel_size_range_max', 'price', 'installer_address']

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
        return instance

class QuoteRequestInstallerForm(forms.ModelForm):
    class Meta:
        model = QuoteRequestInstaller
        fields = ['panel_size_min', 'panel_size_max', 'quote_deadline']

    def __init__(self, *args, **kwargs):
        # Optionally handle any context-specific initialization here
        super().__init__(*args, **kwargs)

        # If there are fields like panel size that should have dynamic initial values, you can add them here
        # Example: Set initial values for 'quote_deadline' to a default date
        self.fields['quote_deadline'].initial = None

class QuoteSubmissionInstallerForm(forms.ModelForm):
    class Meta:
        model = QuoteSubmissionInstaller
        fields = ['price_estimate', 'notes', 'status']

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['price_estimate', 'notes']

class AcceptDeclineQuoteForm(forms.Form):
    action = forms.ChoiceField(
        choices=[('accept', 'Accept'), ('decline', 'Decline')],
        widget=forms.RadioSelect
    )

class SearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=True, label="Search")
    search_type = forms.ChoiceField(choices=[], required=True)

    def __init__(self, user, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        
        if user.profile.user_role == 'customer':
            self.fields['search_type'].choices = [
                ('installer', 'Search Installers'),
                ('product', 'Search Products'),
            ]
        elif user.profile.user_role == 'vendor':
            self.fields['search_type'].choices = [
                ('product', 'Search Products'),
            ]
        elif user.profile.user_role == 'installer':
            self.fields['search_type'].choices = [
                ('install_request', 'Search Installation Requests'),
            ]
        elif user.profile.user_role == 'admin':
            self.fields['search_type'].choices = [
                ('user', 'Search Users'),
                ('install_request', 'Search Install Requests'),
            ]

class SolarEstimationForm(forms.Form):
    postcode = forms.CharField(label="Postcode", max_length=10)
    electricity_bill = forms.DecimalField(label="Monthly Electricity Bill (£)", min_value=0)
    house_type = forms.ChoiceField(
        label="House Type",
        choices=[("detached", "Detached"), ("semi-detached", "Semi-Detached"), ("flat", "Flat")]
    )

    def clean_postcode(self):
        postcode = self.cleaned_data["postcode"]
        if not validate_uk_postcode(postcode):
            raise ValidationError("Invalid UK postcode format.")
        return postcode

    def clean_house_type(self):
        house_type = self.cleaned_data["house_type"]
        if house_type.lower() == "flat":
            raise ValidationError("Solar panel can't be installed on flats.")
        return house_type