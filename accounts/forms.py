"""
This module contains three class forms to create user and update user profile and information, 
 in three forms we are using the User and UserProfile models from the accounts app.
In all three forms, the Meta iiner class is used to specify additional options.
"""

from django import forms
from .models import User, UserProfile
from .validators import allow_only_images_validator


class UserForm(forms.ModelForm):
    """
    A form for creating a new user.

    This form extends the ModelForm class and provides fields for the user's
    first name, last name, username, email, password, and confirm password.

    The clean() method is overridden to validate that the password and confirm
    password fields match.

    Attributes:
        password (CharField): A field for entering the user's password.
        confirm_password (CharField): A field for confirming the user's password.

    Raises:
        ValidationError: If the password and confirm password fields do not match.
    """

    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        """
        Meta class for defining metadata options for the User form.
        
        Attributes:
            model (class): The model class that the form is associated with.
            fields (list): The list of fields to include in the form.
        """
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]

    def clean(self):
        """
        Clean and validate the form data.

        This method is called during form validation and
        is used to clean and validate the form data.
        It compares the password and confirm_password fields and
        raises a ValidationError if they don't match.

        Returns:
            dict: The cleaned form data.

        Raises:
            forms.ValidationError: If the password and confirm_password fields don't match.
        """
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Password does not match!")


class UserProfileForm(forms.ModelForm):
    """
    A form for updating user profile information.

    This form includes fields for profile picture, cover photo, address, country, state,
    city, pin code, latitude, and longitude.

    Attributes:
        profile_picture (FileField): Field for uploading a profile picture.
        cover_photo (FileField): Field for uploading a cover photo.
        address (CharField): Field for entering the user's address.
        country (CharField): Field for entering the user's country.
        state (CharField): Field for entering the user's state.
        city (CharField): Field for entering the user's city.
        pin_code (CharField): Field for entering the user's pin code.
        latitude (CharField): Field for displaying the latitude.
        longitude (CharField): Field for displaying the longitude.
    """

    address = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Start typing...", "required": "required"}
        )
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"placeholder": "Start typing...", "required": "required"}
        ),
    )
    profile_picture = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info"}),
        validators=[allow_only_images_validator],
    )
    cover_photo = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info"}),
        validators=[allow_only_images_validator],
    )

    # latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    class Meta:
        """
        Meta class for defining metadata options for the UserProfile form.
        """

        model = UserProfile
        fields = [
            "profile_picture",
            "cover_photo",
            "address",
            "country",
            "state",
            "city",
            "pin_code",
            "latitude",
            "longitude",
        ]

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == "latitude" or field == "longitude":
                self.fields[field].widget.attrs["readonly"] = "readonly"


class UserInfoForm(forms.ModelForm):
    """
    A form for updating user information.

    This form is used to update the first name, last name, and phone number
    fields of a user.

    Attributes:
        model (User): The User model to be used for the form.
        fields (list): The list of fields to be included in the form.

    """
    class Meta:
        """
        Meta class for defining metadata options for the User form.
        """
        model = User
        fields = ["first_name", "last_name", "phone_number"]
