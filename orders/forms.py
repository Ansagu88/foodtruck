"""
The forms module contains the form classes for the orders app.
We have OrderForm class which is used to create or update an Order object.

"""

from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    """
    A form for creating or updating an order.

    Inherits from `forms.ModelForm` and provides fields for the following order details:
    - first_name
    - last_name
    - phone
    - email
    - address
    - country
    - state
    - city
    - pin_code
    """

    class Meta:
        """
        Meta class for defining metadata options for the Order form.
        """
        model = Order
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "address",
            "country",
            "state",
            "city",
            "pin_code",
        ]
