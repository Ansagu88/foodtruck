"""
In this forms module, we have a form class for creating and updating Vendor 
instances and a form class for creating or updating an OpeningHour instance.
"""
from django import forms
from accounts.validators import allow_only_images_validator
from .models import Vendor, OpeningHour


class VendorForm(forms.ModelForm):
    """
    Form class for creating and updating Vendor instances.

    This form is used to create and update Vendor instances. 
    It includes fields for vendor name and vendor license.
    """

    vendor_license = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info"}),
        validators=[allow_only_images_validator],
    )

    class Meta:
        """
        Meta class for defining metadata options for the Vendor form.

        Attributes:
            model (Vendor): The model class associated with the form.
            fields (list): The list of fields to include in the form.
        """

        model = Vendor
        fields = ["vendor_name", "vendor_license"]


class OpeningHourForm(forms.ModelForm):
    """
    A form for creating or updating an OpeningHour instance.
    """

    class Meta:
        """
        Meta class for defining metadata options for the OpeningHour form.
        """

        model = OpeningHour
        fields = ["day", "from_hour", "to_hour", "is_closed"]
