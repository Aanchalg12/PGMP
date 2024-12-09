from django.core.exceptions import ValidationError
from .models import InstallationBooking

def validate_booking_date(installer, desired_date):
        # Check if the installer has a booking on the desired date
        conflicting_booking = InstallationBooking.objects.filter(
            installer=installer,
            installation_date=desired_date,
            status__in=['pending', 'confirmed']  # Check for conflicting statuses
        ).exists()
    
        if conflicting_booking:
            raise ValidationError("The selected date is not available. Please choose another date.")
