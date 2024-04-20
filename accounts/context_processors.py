"""
This module contains functions to retrieve user and vendor information, 
 and to get Google API and PayPal client ID from settings.
"""

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import UserProfile
from vendor.models import Vendor


def get_vendor(request):
    """
    Retrieves the vendor associated with the current user.

    Args:
        request (HttpRequest): The current request object.

    Returns:
        dict: A dictionary containing the vendor object, or None if no vendor is found.
    """
    vendor = None
    if request.user.is_authenticated:
        try:
            vendor = Vendor.objects.get(user=request.user)
        except ObjectDoesNotExist:
            pass
    return {'vendor': vendor}


def get_user_profile(request):
    """
    Retrieve the user profile associated with the given request.

    Args:
        request (HttpRequest): The request object.

    Returns:
        dict: A dictionary containing the user profile, or None if not found.
    """
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            pass
    return {'user_profile': user_profile}


def get_google_api(request):
    """
    Retrieves the Google API key from the settings and returns it as a context variable.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        dict: A dictionary containing the Google API key as a context variable.

    """
    return {"GOOGLE_API_KEY": settings.GOOGLE_API_KEY}


def get_paypal_client_id(request):
    """
    Retrieves the PayPal client ID from the settings and returns it as a dictionary.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        dict: A dictionary containing the PayPal client ID.

    """
    return {"PAYPAL_CLIENT_ID": settings.PAYPAL_CLIENT_ID}
