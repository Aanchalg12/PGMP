import datetime
from datetime import datetime
import logging
import math
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from .models import InstallationBooking, Profile, Installation, Order, Transaction, RateSetting, Bid, QuoteRequest, Product, SolarEstimation, Installer, CartItem, InstallerService, QuoteSubmission, Quote, QuoteRequestInstaller, QuoteSubmissionInstaller
from .forms import LoginForm, UserEditForm, UserRegistrationForm, QuoteRequestForm, AcceptDeclineQuoteForm, QuoteForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, UserForm, ProfileForm, SignupForm, ProductForm, QuoteSubmissionForm, CartItemForm, InstallationServiceForm, QuoteSubmissionInstallerForm
from django.db import IntegrityError
from django.utils import timezone
from django.http import JsonResponse
from .validators import validate_uk_postcode
import requests
from django.db.models import Q
from django.urls import reverse
from django.db import transaction
from datetime import date
from geopy.distance import geodesic
from solar_estimator.models import QuoteRequest, QuoteSubmission, QuoteSubmissionInstaller
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from solar_estimator.models import QuoteRequest, QuoteRequestInstaller, QuoteSubmission, QuoteSubmissionInstaller
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F

def get_lat_lon_from_address(address):
    # Use a geocoding API to get latitude and longitude from the address
    url = f"https://api.openweathermap.org/data/2.5/weather?q={address}&appid=d95926a4402943eb941d6ab3c2b46a4f"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and 'coord' in data:
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        return lat, lon
    else:
        return None, None

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c
    return distance

@login_required
def add_installation_service(request):
    if request.method == "POST":
        form = InstallationServiceForm(request.POST)
        
        if form.is_valid():
            service = form.save(commit=False)  # Don't save yet; this is a new instance
            service.installer = request.user.profile  # Manually assign the installer to the logged-in user
            service.save()  # Save the service
            return redirect('installer_dashboard')  # Redirect after successful creation
    else:
        form = InstallationServiceForm()

    return render(request, 'add_installation_service.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                # Prepare user instance without saving to database
                user = form.save(commit=False)

                # Check if username is already taken
                if User.objects.filter(username=user.username).exists():
                    messages.error(request, "This username is already taken. Please choose a different one.")
                    return render(request, 'solar_estimator/signup.html', {'form': form})

                # Save the user instance
                user.save()

                # Check if the profile already exists
                if not Profile.objects.filter(user=user).exists():
                    Profile.objects.create(user=user)

                # Log the user in after signup
                auth_login(request, user)

                return redirect('login')

            except IntegrityError as e:
                print(f"Error during profile creation: {str(e)}")
                messages.error(request, "There was an error creating your profile. Please try again.")
                return redirect('signup')

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Log the user in
            messages.success(request, "You are now logged in!")

            # Redirect based on user role
            role = user.profile.user_role  # Assuming the Profile model has a user_role field

            if role == 'admin':
                return redirect('admin_dashboard')
            elif role == 'vendor':
                return redirect('vendor_dashboard')
            elif role == 'installer':
                return redirect('installer_dashboard')
            elif role == 'customer':
                return redirect('customer_dashboard')
            elif role == 'electricity_provider':
                return redirect('provider_dashboard')
            else:
                messages.error(request, "Role not assigned. Redirecting to default dashboard.")
                return redirect('customer_dashboard')  # Default dashboard or any other default page

        else:
            messages.error(request, "Invalid username or password.")  # Display error for invalid form
    else:
        form = LoginForm()  # Show an empty form for GET requests

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)  # Use renamed logout function
    messages.success(request, "Logged out successfully!")
    return redirect('login')

@login_required
def admin_dashboard(request):
    # Calculate counts based on user roles
    customer_count = Profile.objects.filter(user_role='customer').count()
    vendor_count = Profile.objects.filter(user_role='vendor').count()
    installation_count = Profile.objects.filter(user_role='installer').count()
    electricity_provider_count = Profile.objects.filter(user_role='electricity_provider').count()

    # Pass the counts to the template context
    context = {
        'customer_count': customer_count,
        'vendor_count': vendor_count,
        'installation_count': installation_count,
        'electricity_provider_count': electricity_provider_count,
    }

    return render(request, 'admin_dashboard.html', context)

@login_required
def customer_dashboard(request):
    # Get the current user's profile
    profile = request.user.profile

    # Fetch the most recent SolarEstimation for this user
    last_estimation = profile.estimations.order_by('-created_at').first()

    if not last_estimation:
        return render(request, 'customer_dashboard.html', {'error': 'No estimation found.'})

    # Fetch recommended solar products based on the estimated size (panel_size)
    recommended_products = Product.objects.filter(panel_size__gte=last_estimation.estimated_size_kw)

    # Get user's address from the profile
    user_address = profile.address  # Make sure address is available in Profile model
    
    # Find nearby installers based on address substring matching
    nearby_installers = []
    if user_address:
        # Simplify the address by extracting a significant part (e.g., first city/region word)
        user_location_keyword = user_address.split(',')[0].strip()  # Example: "Cambridge" from "Cambridge, UK"
        
        # Find installers whose addresses contain the user's location keyword
        nearby_installers = Profile.objects.filter(
            user_role='installer',
            address__icontains=user_location_keyword
        )

    # Pass all the data to the template
    context = {
        'last_estimation': last_estimation,
        'recommended_products': recommended_products,
        'nearby_installers': nearby_installers,
    }

    return render(request, 'customer_dashboard.html', context)

def search_results(request):
    query = request.GET.get('query', '').strip()
    search_type = request.GET.get('search_type', '')

    # Check if the user is logged in
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the logged-in user's profile and role
    user_profile = request.user.profile
    user_role = user_profile.user_role

    # Define a variable to store results
    results = []

    # Handle search based on user role
    if user_role == 'customer':
        # Customer: Search Installers or Products
        if search_type == 'installer' and query:
            # Search for installers (by name or address)
            results = Profile.objects.filter(
                Q(user_role='installer') & (
                    Q(user__username__icontains=query) | 
                    Q(address__icontains=query)
                )
            )
        elif search_type == 'product' and query:
            # Search for products
            results = Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

    elif user_role == 'vendor':
        # Vendor: Search Products
        if search_type == 'product' and query:
            # Search for products
            results = Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

    elif user_role == 'installer':
        # Installer: Search Installation Requests
        if search_type == 'install_request' and query:
            # Search for installation requests by customer profile username or address
            results = InstallationBooking.objects.filter(
                Q(customer_profile__user__username__icontains=query) |
                Q(customer_profile__address__icontains=query)
            )

    elif user_role == 'admin':
        # Admin: Search Users or Install Requests
        if search_type == 'user' and query:
            # Search for users (by username or email)
            results = Profile.objects.filter(
                Q(user__username__icontains=query) |
                Q(user__email__icontains=query)
            )
        elif search_type == 'install_request' and query:
            # Search for installation requests by customer or address
            results = InstallationBooking.objects.filter(
                Q(customer_profile__user__username__icontains=query) |
                Q(customer_profile__address__icontains=query)
            )

    # Return results to the template
    return render(request, 'search_results.html', {
        'results': results,
        'query': query,
        'search_type': search_type,
    })

@login_required
def request_quote(request, estimation_id):
    try:
        # Fetch the estimation based on the provided ID and ensure it's for the current user
        last_estimation = SolarEstimation.objects.get(id=estimation_id, user=request.user.profile)
    except SolarEstimation.DoesNotExist:
        return redirect('customer_dashboard')  # Redirect to dashboard if no estimation found

    # Fetch products from vendors based on the estimated size
    recommended_products = Product.objects.filter(panel_size__gte=last_estimation.estimated_size_kw)

    if request.method == 'POST':
        # Create the form with the estimation data
        form = QuoteRequestForm(request.POST, user=request.user, estimation=last_estimation)
        if form.is_valid():
            # Save the quote request
            quote_request = form.save(commit=False)
            quote_request.customer_profile = request.user.profile  # Correctly assign the Profile to customer_profile
            quote_request.estimation_details = f"Estimated Solar Panel Size: {last_estimation.estimated_size_kw} kW"
            quote_request.save()
            return redirect('customer_dashboard')  # Redirect after form submission
    else:
        # Create the form with initial data
        form = QuoteRequestForm(user=request.user, estimation=last_estimation)

    return render(request, 'request_quote.html', {
        'form': form,
        'last_estimation': last_estimation,
        'recommended_products': recommended_products,
    })

@login_required
def vendor_dashboard(request):
    vendor_profile = request.user.profile  # Get the Profile of the logged-in User
    
    # Query for products and orders associated with the vendor's profile
    products = Product.objects.filter(vendor_profile=vendor_profile)
    active_orders = Order.objects.filter(product__vendor_profile=vendor_profile)
    
    # Query for QuoteRequests based on the customer profile's user role
    quote_requests = QuoteRequest.objects.filter(customer_profile__user_role='customer')

    return render(request, 'vendor_dashboard.html', {
        'products': products,
        'active_orders': active_orders,
        'quote_requests': quote_requests
    })

@login_required
def view_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    total_price = order.product.price * order.quantity
    return render(request, 'order_details.html', {'order': order, 'total_price': total_price})

import logging
logger = logging.getLogger(__name__)

@login_required
def update_order_status(request, order_id):
    # Retrieve the order or return a 404 error if it doesn't exist
    order = get_object_or_404(Order, id=order_id)

    # Example: If `exception_notes` is part of the order, include it in the context
    exception_notes = order.exception_notes if hasattr(order, 'exception_notes') else None

    if request.method == 'POST':
        # Get the new status from POST data
        new_status = request.POST.get('status')

        # List of valid status options
        valid_statuses = ['pending', 'shipped', 'delivered']

        # If a new status is provided and is valid, update and save the order status
        if new_status and new_status in valid_statuses:
            order.status = new_status
            order.save()

            # If the request is AJAX, return a JsonResponse
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"message": "Order status updated successfully"}, status=200)
            
            # If not an AJAX request, redirect to order details page
            return redirect('order_details', order_id=order.id)
        
        # If no new status is provided or it's invalid, respond with an error message
        return JsonResponse({"error": "Invalid status provided or no status provided in POST data"}, status=400)

    elif request.method == 'GET':
        # For GET requests, render the update order status template
        return render(request, 'update_order_status.html', {
            'order': order,
            'exception_notes': exception_notes
        })

    # Fallback response if the request method is neither GET nor POST
    return JsonResponse({"error": "Invalid method. This view supports only GET and POST requests."}, status=405)

@login_required
def order_details(request, order_id):
    # Get the order by ID, including related customer_profile, vendor_profile, and product
    order = get_object_or_404(Order.objects.select_related('customer_profile', 'vendor_profile', 'product'), id=order_id)
    
    # Calculate total price (product price * quantity)
    if order.product and order.product.price:  # Ensure the product exists and has a price
        total_price = order.product.price * order.quantity
    else:
        total_price = 0  # Default in case product or price is missing

    return render(request, 'order_details.html', {
        'order': order,
        'total_price': total_price,  # Pass calculated price to the template
    })

@login_required
def add_product(request):
    # Get the vendor profile of the current user if they are a vendor or an admin
    if request.user.profile.user_role in ['vendor', 'admin']:
        # If the user is an admin, you may want to set the vendor profile differently
        vendor_profile = request.user.profile if request.user.profile.user_role == 'vendor' else None
    else:
        return redirect('unauthorized_access')  # Redirect if the user is not a vendor or admin

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if vendor_profile:
                product.vendor_profile = vendor_profile  # Assign vendor profile for vendors
            product.save()
            return redirect('vendor_dashboard')  # Redirect to the vendor dashboard after saving
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})

@login_required
def edit_product(request, product_id):
    # Retrieve the product or return a 404 error if it doesn't exist
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('vendor_dashboard')  
        else:
            messages.error(request, 'There was an error updating the product.')
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    # Retrieve the product by ID, or return a 404 error if not found
    product = get_object_or_404(Product, id=product_id)

    # Check if the request method is POST
    if request.method == "POST":
        product.delete()  # Delete the product
        messages.success(request, "Product deleted successfully!")  # Add a success message
        return redirect('vendor_dashboard')  # Redirect to the vendor dashboard

    return render(request, 'confirm_delete.html', {'product': product})

def view_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Retrieve the product
    return render(request, 'view_product.html', {'product': product})

def not_authorized(request):
    return render(request, 'not_authorized.html')

@login_required
def submit_quote(request, quote_request_id):
    quote_request = get_object_or_404(QuoteRequest, id=quote_request_id)

    if request.method == 'POST':
        form = QuoteSubmissionForm(request.POST)
        if form.is_valid():
            quote_submission = form.save(commit=False)
            quote_submission.vendor = request.user.profile  # Assuming Profile model has user link
            quote_submission.quote_request = quote_request
            quote_submission.save()
            return redirect('vendor_dashboard')  # Redirect to vendor's dashboard or success page
    else:
        form = QuoteSubmissionForm()

    return render(request, 'submit_quote.html', {
        'form': form,
        'quote_request': quote_request,
    })

@login_required
def customer_quotes(request):
    # Get the current user's profile (customer)
    customer_profile = request.user.profile

    # Fetch all `QuoteRequest` instances for this customer
    quote_requests = QuoteRequest.objects.filter(customer_profile=customer_profile)
    print(f"Quote Requests: {quote_requests}")

    # Vendor quotes based on `QuoteRequest` instances
    vendor_quotes = QuoteSubmission.objects.filter(quote_request__in=quote_requests, vendor__isnull=False)
    print(f"Vendor Quotes: {vendor_quotes}")

    # Fetch all `QuoteRequestInstaller` instances for this customer
    quote_request_installers = QuoteRequestInstaller.objects.filter(customer_profile=customer_profile)
    print(f"Installer Requests: {quote_request_installers}")

    # Installer submissions related to `QuoteRequestInstaller`
    installer_quotes = QuoteSubmissionInstaller.objects.filter(quote_request_installer__in=quote_request_installers)
    print(f"Installer Quotes: {installer_quotes}")

    context = {
        'vendor_quotes': vendor_quotes,
        'installer_quotes': installer_quotes,
    }

    return render(request, 'customer_quotes.html', context)


@login_required
def accept_quote(request, quote_id):
    quote_submission = get_object_or_404(QuoteSubmission, id=quote_id)

    # Ensure the quote belongs to the current customer's request
    if quote_submission.quote_request.customer_profile.user != request.user:
        messages.error(request, "You are not authorized to accept this quote.")
        return redirect('customer_dashboard')

    # Check if the quote has expired
    if quote_submission.quote_request.quote_deadline < timezone.now().date():
        quote_submission.status = 'expired'  # Mark as expired
        quote_submission.save()
        messages.error(request, "This quote has expired and cannot be accepted.")
        return redirect('customer_quotes')

    # Accept the quote
    quote_submission.status = 'accepted'
    quote_submission.save()

    # Decline all other quotes for this request
    QuoteSubmission.objects.filter(quote_request=quote_submission.quote_request).exclude(id=quote_id).update(status='declined')

    messages.success(request, "Quote accepted successfully!")
    return redirect('customer_quotes')

@login_required
def decline_quote(request, quote_id):
    quote_submission = get_object_or_404(QuoteSubmission, id=quote_id)

    # Ensure the quote belongs to the current customer's request
    if quote_submission.quote_request.customer_profile.user != request.user:
        messages.error(request, "You are not authorized to decline this quote.")
        return redirect('customer_dashboard')

    # Check if the quote has expired
    if quote_submission.quote_request.quote_deadline < timezone.now().date():
        quote_submission.status = 'expired'  # Mark as expired
        quote_submission.save()
        messages.error(request, "This quote has expired and cannot be declined.")
        return redirect('customer_quotes')

    # Decline the quote
    quote_submission.status = 'declined'
    quote_submission.save()

    messages.success(request, "Quote declined successfully!")
    return redirect('customer_quotes')

def get_lat_lon_from_postcode(postcode):
    # Use postcode.io to convert postcode to latitude and longitude
    url = f"https://api.postcodes.io/postcodes/{postcode}"
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200 and 'result' in data:
        return data['result']['latitude'], data['result']['longitude']
    return None, None

def get_solar_irradiance(latitude, longitude):
    """
    Fetches daily solar irradiance data for an entire year from NASA's POWER API.
    Returns the yearly average irradiance in kWh/m²/day.
    """
    year = datetime.datetime.now().year
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?"
    params = {
        "start": f"{year}0101",  # Start of the current year
        "end": f"{year}1231",    # End of the current year
        "latitude": latitude,
        "longitude": longitude,
        "parameters": "ALLSKY_SFC_SW_DWN",
        "community": "AG",
        "format": "JSON",
        "userId": "c5xQdgVxnCPEaTqcFXhGf9GIwHAcIfzGcFemcYPH"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print("Error fetching data from NASA POWER API:", response.text)
        return None

    data = response.json()
    
    # Extract and process irradiance data for the full year
    if 'properties' in data and 'parameter' in data['properties']:
        irradiance_data = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        
        # Calculate the average daily irradiance across the year, ignoring missing data
        daily_values = [value for value in irradiance_data.values() if value != -999.0]
        if daily_values:
            average_irradiance = sum(daily_values) / len(daily_values)
            print(f"Calculated average irradiance: {average_irradiance}")  # Debugging output
            return average_irradiance  # Average daily irradiance for the year
        else:
            print("No valid irradiance data found in response.")
            return None
    else:
        print("Unexpected response structure:", data)
        return None

# Adjust these based on typical solar panel costs and efficiency for your area
INSTALLATION_COST_PER_KW = 1200  # Estimated cost per kW of installed solar panels in £
ELECTRICITY_RATE_PER_KWH = 0.25  # Average cost of electricity per kWh in £
ANNUAL_SAVINGS_PERCENTAGE = 0.6  # Percentage of electricity savings assumed

def calculate_solar_panel_size(electricity_bill, solar_irradiance):
    """
    Estimates the required solar panel size based on the user's electricity bill
    and average daily solar irradiance, rounded to the nearest whole kW.
    Also calculates savings and payback period.
    """
    # Convert the monthly electricity bill to annual consumption (in £)
    annual_bill = electricity_bill * 12  # in £

    # Estimate the annual electricity consumption in kWh
    annual_consumption_kwh = annual_bill / ELECTRICITY_RATE_PER_KWH

    # Target 60% of annual electricity consumption
    target_consumption_kwh = annual_consumption_kwh * ANNUAL_SAVINGS_PERCENTAGE

    # Efficiency of the solar panels
    efficiency_factor = 0.18

    # Calculate required area (m²) to meet the 60% consumption based on irradiance
    required_area_m2 = target_consumption_kwh / (solar_irradiance * 365 * efficiency_factor)

    # Convert to solar panel capacity (kW), rounding up to ensure coverage
    panel_size_kw = required_area_m2 * 0.3
    rounded_panel_size_kw = math.ceil(panel_size_kw)

    # Calculate the estimated annual savings on the electricity bill
    annual_savings = target_consumption_kwh * ELECTRICITY_RATE_PER_KWH

    # Calculate the installation cost for the solar panels
    installation_cost = rounded_panel_size_kw * INSTALLATION_COST_PER_KW

    # Calculate the estimated payback period (years)
    payback_period_years = installation_cost / annual_savings if annual_savings else float('inf')

    return {
        "panel_size_kw": rounded_panel_size_kw,
        "annual_savings": round(annual_savings, 2),
        "installation_cost": installation_cost,
        "payback_period_years": round(payback_period_years, 2)
    }

def estimate_solar_size(request):
    if request.method == "POST":
        postcode = request.POST.get("postcode")
        postcode = postcode.strip().replace(" ", "").upper()

        # Validate postcode format
        if not validate_uk_postcode(postcode):
            return JsonResponse({"error": "Invalid UK postcode format."})

        # Retrieve and validate the electricity bill
        electricity_bill = request.POST.get("electricity_bill")
        try:
            electricity_bill = float(electricity_bill)
            if electricity_bill <= 0:
                raise ValueError("Electricity bill must be a positive number.")
        except ValueError:
            return JsonResponse({"error": "Electricity bill must be a positive number."})

        # Check if house type is suitable for solar panel installation
        house_type = request.POST.get("house_type")
        if house_type.lower() == "flat":
            return JsonResponse({"error": "Solar panels cannot be installed on flats."})

        # Fetch latitude and longitude based on the postcode
        latitude, longitude = get_lat_lon_from_postcode(postcode)
        solar_irradiance = get_solar_irradiance(latitude, longitude)
        
        if not solar_irradiance:
            return JsonResponse({"error": "Unable to retrieve solar irradiance data."})

        # Calculate solar panel size, savings, and payback period
        calculations = calculate_solar_panel_size(electricity_bill, solar_irradiance)

        # Store values in session for display on the result page
        request.session['longitude'] = longitude
        request.session['latitude'] = latitude
        request.session['solar_irradiance'] = round(solar_irradiance, 2)
        request.session['estimated_size_kw'] = calculations["panel_size_kw"]
        request.session['annual_savings'] = calculations["annual_savings"]
        request.session['installation_cost'] = calculations["installation_cost"]
        request.session['payback_period_years'] = calculations["payback_period_years"]

        # Save the estimation result to the database if the user is authenticated
        if request.user.is_authenticated:
            try:
                # Fetch the Profile associated with the authenticated user
                profile = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                return JsonResponse({"error": "Profile does not exist for the user."})

            # Create the SolarEstimation with the Profile instance
            SolarEstimation.objects.create(
                user=profile,  # Use the Profile instance here
                postcode=postcode,
                longitude=longitude,
                latitude=latitude,
                electricity_bill=electricity_bill,
                house_type=house_type,
                solar_irradiance=solar_irradiance,
                estimated_size_kw=calculations["panel_size_kw"],
                annual_savings=calculations["annual_savings"],  # Added field for annual savings
                payback_period=calculations["payback_period_years"]  # Added field for payback period
            )

        # Redirect to the result page
        return redirect(reverse('estimation_result'))

    return render(request, "estimate_solar_size.html")

def estimation_result(request):
    # Fetch the data from session
    longitude = request.session.get('longitude')
    latitude = request.session.get('latitude')
    solar_irradiance = request.session.get('solar_irradiance')
    estimated_size_kw = request.session.get('estimated_size_kw')
    annual_savings = request.session.get('annual_savings')
    installation_cost = request.session.get('installation_cost')
    payback_period_years = request.session.get('payback_period_years')

    # If required data is missing, redirect to the estimation form
    if not all([longitude, latitude, solar_irradiance, estimated_size_kw, annual_savings, installation_cost, payback_period_years]):
        return redirect('estimate_solar_size')

    # Pass the values to the template
    return render(request, 'estimation_result.html', {
        'longitude': longitude,
        'latitude': latitude,
        'solar_irradiance': solar_irradiance,
        'estimated_size_kw': estimated_size_kw,
        'annual_savings': annual_savings,
        'installation_cost': installation_cost,
        'payback_period_years': payback_period_years
    })

def view_estimations(request):
    estimations = SolarEstimation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "view_estimations.html", {"estimations": estimations})

def product_vendors(request):
    # Fetch all products and pass them to the template
    products = Product.objects.all()

    # Prepare context with products to render in the template
    context = {
        'products': products
    }

    return render(request, 'product_vendors.html', context)

@login_required
def add_to_cart(request, product_id):
    # Get the product based on the ID
    product = Product.objects.get(id=product_id)

    # Check if the customer is logged in and has a profile
    if request.user.profile.user_role != 'customer':
        return redirect('home')  # Or handle this appropriately

    # Add the product to the cart (or update quantity if already in cart)
    cart_item, created = CartItem.objects.get_or_create(
        customer_profile=request.user.profile,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Redirect to the shopping_cart page after adding the product
    return redirect('shopping_cart')  # Change 'cart' to 'shopping_cart'

@login_required
def remove_from_cart(request, item_id):
    # Get the cart item based on the provided ID
    cart_item = get_object_or_404(CartItem, id=item_id, customer_profile=request.user.profile)
    
    # Delete the cart item
    cart_item.delete()
    
    # After removing, redirect back to the shopping cart
    return redirect('shopping_cart')

@login_required
def checkout(request):
    # Get the current user's cart items
    cart_items = CartItem.objects.filter(customer_profile=request.user.profile)

    if not cart_items.exists():
        return redirect('shopping_cart')  # If cart is empty, redirect to shopping cart

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        with transaction.atomic():  # Ensure atomic transaction
            for item in cart_items:
                # Create the order and associate it with the customer and vendor
                order = Order.objects.create(
                    customer_profile=request.user.profile,
                    vendor_profile=item.product.vendor_profile,  # Link to vendor profile
                    product=item.product,
                    quantity=item.quantity,
                    status='pending',  # Order status is 'pending'
                    order_date=date.today(),
                )
                # Delete the cart item after creating the order
                item.delete()

        # Redirect to 'my_orders' page after placing the order
        return redirect('my_orders')  # Redirect to the page where the user can view their orders

    # Render the checkout page with cart items and total price
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

@login_required
def my_orders(request):
    # Fetch all orders related to the logged-in customer
    orders = Order.objects.filter(customer_profile=request.user.profile)

    # Prepare orders with computed total price (product price * quantity)
    order_details = []
    for order in orders:
        total_price = order.product.price * order.quantity
        order_details.append({
            'order': order,
            'total_price': total_price
        })

    # Fetch installation bookings for the customer
    installations = InstallationBooking.objects.filter(customer_profile=request.user.profile)

    # Pass both orders and installations to the template
    return render(request, 'my_orders.html', {
        'order_details': order_details,
        'installations': installations  # Add installations to the context
    })


def edit_cart_item(request, item_id):
    # Get the CartItem object
    cart_item = get_object_or_404(CartItem, id=item_id)

    # If the form is submitted via POST
    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=cart_item)
        if form.is_valid():
            # Save the changes to the cart item
            form.save()
            return redirect('shopping_cart')  # Redirect to the shopping cart after saving
    else:
        # If it's a GET request, show the current cart item data in the form
        form = CartItemForm(instance=cart_item)

    return render(request, 'edit_cart_item.html', {'form': form})

def order_confirmation(request):
    # Retrieve orders based on the logged-in user
    orders = Order.objects.filter(customer_profile=request.user.profile, status='pending')
    return render(request, 'order_confirmation.html', {'orders': orders})

@login_required
def shopping_cart(request):
    # Get the cart items for the logged-in user
    cart_items = CartItem.objects.filter(customer_profile=request.user.profile)
    
    # Calculate the total price of items in the cart
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    
    # Render the shopping cart page with the cart items and total price
    return render(request, 'shopping_cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def provider_dashboard(request):
    if request.user.profile.user_role != 'electricity_provider':
        return redirect('home')  # Redirect if not an electricity provider

    # Fetch active and withdrawn bids
    active_bids = Bid.objects.filter(provider_profile=request.user.profile, status='active')
    completed_transactions = Transaction.objects.filter(provider_profile=request.user.profile).order_by('-date')

    # Get or create rate setting
    rate_setting, created = RateSetting.objects.get_or_create(provider_profile=request.user.profile)

    # Check if the effective date for a new rate has arrived or passed, update current rate if so
    if rate_setting.effective_date and rate_setting.effective_date <= timezone.now().date():
        if rate_setting.new_buyback_rate:
            rate_setting.current_buyback_rate = rate_setting.new_buyback_rate
            rate_setting.new_buyback_rate = None  # Reset new rate after applying it
            rate_setting.effective_date = None  # Reset effective date after applying it
            rate_setting.save()

    # Handle form submission for updating the rate
    if request.method == 'POST' and 'update_rate' in request.POST:
        new_rate = request.POST.get('new_buyback_rate')
        effective_date = request.POST.get('effective_date')
        
        if new_rate and effective_date:
            rate_setting.new_buyback_rate = new_rate
            rate_setting.effective_date = effective_date
            rate_setting.save()
            messages.success(request, "Buyback rate updated successfully.")
        else:
            messages.error(request, "Please provide a valid rate and effective date.")

    context = {
        'active_bids': active_bids,
        'completed_transactions': completed_transactions,
        'rate_setting': rate_setting,
    }
    return render(request, 'provider_dashboard.html', context)

@login_required
def view_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id, provider_profile=request.user.profile)
    return render(request, 'view_bid.html', {'bid': bid})

@login_required
def edit_bid(request, bid_id):
    # Add logic to edit the bid amount or expiration date
    pass

@login_required
def withdraw_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id, provider_profile=request.user.profile)
    bid.status = 'withdrawn'
    bid.save()
    messages.success(request, "Bid withdrawn successfully.")
    return redirect('provider_dashboard')

@login_required
def user_management(request):
    if not request.user.is_staff:  # Only allow access to admin or staff users
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')

    # Fetch all users with their profiles (using select_related for optimization)
    users = User.objects.select_related('profile').all()

    return render(request, 'user_management.html', {'users': users})

logger = logging.getLogger(__name__)

@login_required
def add_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()  # This will create or update the user and profile
                messages.success(request, "User added successfully!")
                return redirect('user_management')
            except Exception as e:
                logger.error(f"Error saving user or profile: {e}")
                messages.error(request, "There was an error with the form. Please try again.")
        else:
            logger.error("Form is not valid: %s", form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'add_user.html', {'form': form})

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect('user_management')

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, created = Profile.objects.get_or_create(user=user)  # Ensure Profile exists
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_detail', user_id=user.id)
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'edit_user.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user
    })

@login_required
def user_detail(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    return render(request, 'user_detail.html', {'profile': profile})

@login_required
def profile(request):
    # Ensure the user has a profile, if not create one
    if not Profile.objects.filter(user=request.user).exists():
        Profile.objects.create(user=request.user)

    # Create forms with the user's data
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)

    if request.method == 'POST':
        # Re-initialize the forms with POST data and files
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)  # Include request.FILES

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # Save the user information
            profile_form.save()  # Save the profile, including profile picture
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required
def settings(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Settings updated successfully.")
            return redirect('settings')
        else:
            messages.error(request, "Please correct the errors below.")
    
    else:
        user_form = UserForm(instance=request.user)

    return render(request, 'settings.html', {
        'user_form': user_form,
    })

@login_required
def reports(request):
        # Check if the user is an admin
    if request.user.profile.user_role != 'admin':
        return redirect('not_authorized')  # Or handle unauthorized access differently

    # Get any filtering parameters from GET request (optional filters)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status_filter = request.GET.get('status')

    # Initialize the queryset to all installation bookings
    installations = InstallationBooking.objects.all()

    # Apply filters based on query parameters (if provided)
    if start_date:
        installations = installations.filter(installation_date__gte=start_date)
    if end_date:
        installations = installations.filter(installation_date__lte=end_date)
    if status_filter:
        installations = installations.filter(status=status_filter)

    # You can also aggregate data, like how many installations are in each status
    installations_count_by_status = installations.values('status').annotate(count=Count('status'))

    # For overall stats (e.g., total installations)
    total_installations = installations.count()
    pending_installations = installations.filter(status='pending').count()
    completed_installations = installations.filter(status='completed').count()
    
    # Render the report template with necessary data
    return render(request, 'reports.html', {
        'installations': installations,
        'installations_count_by_status': installations_count_by_status,
        'total_installations': total_installations,
        'pending_installations': pending_installations,
        'completed_installations': completed_installations,
        'start_date': start_date,
        'end_date': end_date,
        'status_filter': status_filter,
    })

def home(request):
    return render(request, 'home.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

@login_required
def installation_services(request):
    # Get the user's profile instance
    user_profile = request.user.profile

    # Fetch all services to display to the customer
    services = InstallerService.objects.all()

    # Retrieve the last solar estimation associated with the user's profile
    last_estimation = SolarEstimation.objects.filter(user=user_profile).last()

    # Pass both services and last estimation to the template
    return render(request, 'installation_services.html', {
        'services': services,
        'last_estimation': last_estimation
    })

@login_required
def book_service(request, service_id):
    service = get_object_or_404(InstallerService, id=service_id)
    user_profile = request.user.profile

    # Fetch the first QuoteSubmissionInstaller related to the installer for this service
    quote_submission_installer = QuoteSubmissionInstaller.objects.filter(installer=service.installer).first()

    if not quote_submission_installer:
        messages.error(request, "No quote submission found for this installer.")
        return redirect('customer_dashboard')  # Adjust this to a relevant page

    # Create an InstallationBooking object
    installation_booking = InstallationBooking.objects.create(
        quote_submission_installer=quote_submission_installer,
        installer=service.installer,
        customer_profile=user_profile,
        solar_panel_size=1.0,  # Adjust this based on user selection
        installation_date=datetime.now(),  # You can use a different date if needed
        status='pending',  # Default status
    )

    # Show a success message
    messages.success(request, "Service booked successfully. Your request is now pending approval from the installer.")

    # Redirect to My Orders (the page showing the customer's orders)
    return redirect('my_orders')

def install_request_detail(request, id):
    # Fetch the installation booking by ID
    installation_booking = get_object_or_404(InstallationBooking, id=id)
    
    # Pass the installation booking to the template
    return render(request, 'install_request_detail.html', {'installation_booking': installation_booking})

@login_required
def submit_installer_quote(request, quote_request_installer_id):
    # Get the QuoteRequestInstaller object
    quote_request_installer = QuoteRequestInstaller.objects.get(id=quote_request_installer_id)

    # Only allow installers to submit quotes
    if request.user.profile.user_role != 'installer':
        return redirect('home')

    if request.method == 'POST':
        form = QuoteSubmissionInstallerForm(request.POST)
        if form.is_valid():
            # Save the QuoteSubmissionInstaller instance
            quote_submission = form.save(commit=False)
            quote_submission.quote_request_installer = quote_request_installer
            quote_submission.installer = request.user.profile
            quote_submission.save()

            # Now, create or update the Quote object for this QuoteRequestInstaller and the installer
            quote, created = Quote.objects.get_or_create(
                quote_request=quote_request_installer,
                installer_profile=request.user.profile  # Use the current installer
            )

            # Update the Quote object with the data from QuoteSubmissionInstaller
            quote.price_estimate = quote_submission.price_estimate
            quote.notes = quote_submission.notes
            quote.status = quote_submission.status  # Update status as well (if required)
            quote.save()

            # Redirect after saving the quote
            return redirect('customer_dashboard')  # Or wherever you want to redirect

    else:
        form = QuoteSubmissionInstallerForm()

    return render(request, 'submit_installer_quote.html', {'form': form})

@login_required
def accept_installation(request, quote_submission_id):
    # Retrieve the QuoteSubmissionInstaller instance
    quote_submission = get_object_or_404(QuoteSubmissionInstaller, id=quote_submission_id)

    # Ensure the quote belongs to the current customer's request
    if quote_submission.quote_request_installer.customer_profile.user != request.user:
        messages.error(request, "You are not authorized to accept this quote.")
        return redirect('customer_dashboard')

    # Update the quote status to accepted
    quote_submission.status = 'accepted'
    quote_submission.save()

    # Create an installation booking for the accepted quote
    # Here we assume the customer wants the installation booked immediately, so we use a fixed installation date
    booking_date = timezone.now()  # You can change this to a specific date or allow the user to choose

    installation_booking = InstallationBooking.objects.create(
        quote_submission_installer=quote_submission,
        installer=quote_submission.installer,  # The installer from the quote submission
        installation_date=booking_date,
        status='booked'  # Status when the booking is confirmed
    )

    messages.success(request, "Quote accepted and installer booked successfully!")
    return redirect('customer_quotes')


@login_required
def decline_installation(request, quote_submission_id):
    # Retrieve the quote submission for the installer or return a 404 if not found
    quote_submission = get_object_or_404(QuoteSubmissionInstaller, id=quote_submission_id)

    # Ensure the quote submission is part of the customer's request
    if quote_submission.quote_request_installer.customer_profile.user != request.user:
        messages.error(request, "You are not authorized to decline this quote.")
        return redirect('customer_dashboard')

    # Ensure the quote is not expired
    if quote_submission.quote_request_installer.quote_deadline < timezone.now().date():
        messages.error(request, "This quote has expired and cannot be declined.")
        return redirect('customer_quotes')

    # Decline the quote and update its status
    quote_submission.status = 'declined'
    quote_submission.save()

    messages.success(request, "Quote declined successfully!")
    return redirect('customer_quotes')
    
@login_required
def get_quote(request, estimation_id):
    # Get the profile of the logged-in customer
    customer_profile = request.user.profile
    
    # Fetch the SolarEstimation instance using the correct field name
    estimation = get_object_or_404(SolarEstimation, id=estimation_id, user=customer_profile)
    
    # Use the `estimated_size_kw` field directly
    quote_request = QuoteRequestInstaller.objects.create(
        customer_profile=customer_profile,
        panel_size_min=estimation.estimated_size_kw,  # Use estimated_size_kw as both min and max if needed
        panel_size_max=estimation.estimated_size_kw,  # Or set a range if appropriate
        quote_deadline=timezone.now() + timedelta(days=7),  # example deadline
        status='pending'
    )
    
    # Create a quote entry for each installer
    installer_services = InstallerService.objects.all()
    for service in installer_services:
        Quote.objects.create(
            quote_request=quote_request,
            installer_profile=service.installer,
            status='pending'
        )

    # Render a confirmation page with installer service details
    return render(request, 'quote_request.html', {
        'installer_services': installer_services,
    })

@login_required
def installation_dashboard(request):
    profile = request.user.profile

    # Fetch relevant data for the installer's dashboard
    installation_services = InstallerService.objects.filter(installer=profile)
    pending_installations = InstallationBooking.objects.filter(installer=profile, status='pending')
    scheduled_installations = Installation.objects.exclude(scheduled_date__isnull=True).order_by('scheduled_date')

    # Show only pending quote requests for this installer
    pending_quotes = Quote.objects.filter(installer_profile=profile, status='pending')
    quotes_submitted = Quote.objects.filter(installer_profile=profile)

    return render(request, 'installer_dashboard.html', {
        'installation_services': installation_services,
        'pending_installations': pending_installations,
        'scheduled_installations': scheduled_installations,
        'quotes_submitted': quotes_submitted,
        'pending_quotes': pending_quotes,  # Quotes awaiting installer response
    })

@login_required
def respond_to_quote(request, quote_request_id):
    quote_request_installer = get_object_or_404(QuoteRequestInstaller, id=quote_request_id)
    installer_profile = request.user.profile

    # Check if a submission already exists for this installer and quote request
    existing_submission = QuoteSubmissionInstaller.objects.filter(
        installer=installer_profile,
        quote_request_installer=quote_request_installer
    ).first()

    if existing_submission:
        messages.error(request, "You have already submitted a quote for this request.")
        return redirect('installer_dashboard')

    if request.method == 'POST':
        price_estimate = request.POST.get('price_estimate')
        notes = request.POST.get('notes')

        # Create and save the QuoteSubmissionInstaller
        quote_submission_installer = QuoteSubmissionInstaller.objects.create(
            quote_request_installer=quote_request_installer,
            installer=installer_profile,
            price_estimate=price_estimate,
            notes=notes,
            submitted_at=timezone.now(),
            status='pending'
        )

        messages.success(request, "Quote submitted successfully!")
        return redirect('installer_dashboard')

    return render(request, 'respond_to_quote.html', {'quote_request': quote_request_installer})

@login_required
def update_installation_service(request, service_id):
    # Fetch the service object to be updated
    service = get_object_or_404(InstallerService, id=service_id, installer=request.user.profile)

    if request.method == 'POST':
        form = InstallationServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('installer_dashboard')  # Redirect to the installer dashboard after saving
    else:
        form = InstallationServiceForm(instance=service)

    return render(request, 'update_installation_service.html', {'form': form, 'service': service})

@login_required
def view_installation_service(request, service_id):
    service = get_object_or_404(InstallerService, id=service_id, installer=request.user.profile)
    return render(request, 'view_installation_service.html', {'service': service})

def update_installation_status(request, installation_id, status):
    installation = get_object_or_404(InstallationBooking, id=installation_id)
    installation.status = status
    installation.save()
    return redirect('install_requests')

@login_required
def delete_installation_service(request, service_id):
    # Retrieve the service by its ID or return a 404 if not found
    service = get_object_or_404(InstallerService, id=service_id)
    
    # Ensure only the installer (user) who created the service can delete it
    if service.installer.user == request.user:
        service.delete()
        # Redirect to the installer dashboard after deletion
        return redirect('installer_dashboard')
    
    # Optionally, you can return a 403 Forbidden error if the user is not allowed to delete this service
    return redirect('installer_dashboard')

@login_required
def installation_detail(request, installation_id):
    # Get the installation object or return a 404 if it doesn't exist
    installation = get_object_or_404(Installation, id=installation_id)
    
    # Check permissions if needed, e.g., only the customer or admin can view
    if request.user.profile.user_role == 'customer' and installation.customer_profile != request.user.profile:
        return redirect('not_authorized')  # Redirect if the user isn't allowed to view this

    return render(request, 'installation_detail.html', {
        'installation': installation,
    })

@login_required
def install_requests(request):
    # Check user role
    print(f"User role: {request.user.profile.user_role}")  # Debugging line to check the role

    # Check if the user is an installer or an admin
    if request.user.profile.user_role not in ['installer', 'admin']:
        print("Access Denied: Unauthorized role.")  # Debugging line to check access denial
        return redirect('not_authorized')  # Or handle unauthorized access differently

    # Query for pending installations, including both installers and admins
    if request.user.profile.user_role == 'installer':
        # For installers, filter only their own pending installations
        installations = InstallationBooking.objects.filter(installer=request.user.profile, status='pending')
    elif request.user.profile.user_role == 'admin':
        # For admins, show all pending installations
        installations = InstallationBooking.objects.filter(status='pending')

    # Render the installations to the template
    return render(request, 'install_requests.html', {'installations': installations})

@login_required
def transactions(request):
    # Allow access for both electricity provider and admin users
    if request.user.profile.user_role not in ['electricity_provider', 'admin']:
        return redirect('not_authorized')  # Redirect if the user is not an electricity provider or admin

    # Fetch transactions for this provider, or all transactions if the user is an admin
    if request.user.profile.user_role == 'electricity_provider':
        transactions = Transaction.objects.filter(provider_profile=request.user.profile)
    else:
        transactions = Transaction.objects.all()  # Admins can view all transactions

    return render(request, 'transactions.html', {'transactions': transactions})

@login_required
def orders(request):
    # Allow access for both vendor and admin users
    if request.user.profile.user_role not in ['vendor', 'admin']:
        return redirect('not_authorized')  # Redirect if the user is not a vendor or admin

    # Fetch orders for the vendor or all orders if the user is an admin
    if request.user.profile.user_role == 'vendor':
        orders = Order.objects.filter(vendor_profile=request.user.profile)
    else:
        orders = Order.objects.all()  # Admins can view all orders

    return render(request, 'orders.html', {'orders': orders})

@login_required
def estimator(request):
    if request.user.profile.user_role != 'customer':
        return redirect('not_authorized')

    # Basic form setup or query information needed for estimator
    if request.method == 'POST':
        # Handle the estimator form submission
        pass

    return render(request, 'estimation.html')