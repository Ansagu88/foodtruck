"""
The forms module contains the form classes for the menu app.
We have two form classes: CategoryForm and FoodItemForm.

"""
from django import forms

from accounts.validators import allow_only_images_validator
from .models import Category, FoodItem


class CategoryForm(forms.ModelForm):
    """
    A form for creating or updating a Category.

    This form is used to create or update a Category object. 
    It includes fields for the category name and description.

    Attributes:
        category_name (str): The name of the category.
        description (str): The description of the category.

    """
    class Meta:
        """
        Meta class for defining metadata options for the Category form.
        """
        model = Category
        fields = ["category_name", "description"]


class FoodItemForm(forms.ModelForm):
    """
    A form for creating or updating a FoodItem.

    This form includes fields for the category, food title, description, price, image, 
    and availability status of a food item.

    Attributes:
        image (FileField): A field for uploading an image file.

    Meta:
        model (FoodItem): The model associated with this form.
        fields (list): The fields to include in the form.
    """

    image = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info w-100"}),
        validators=[allow_only_images_validator],
    )

    class Meta:
        """
        Meta class for defining metadata options for the FoodItem form.
        """

        model = FoodItem
        fields = [
            "category",
            "food_title",
            "description",
            "price",
            "image",
            "is_available",
        ]
