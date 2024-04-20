"""
In the menu app, the models module contains the Category and FoodItem models.

"""
from django.db import models
from vendor.models import Vendor


class Category(models.Model):
    """
    Represents a category for food items in a food truck menu.

    Attributes:
        vendor (ForeignKey): The vendor associated with the category.
        category_name (CharField): The name of the category.
        slug (SlugField): The slug field for the category.
        description (TextField): The description of the category.
        created_at (DateTimeField): The date and time when the category was created.
        updated_at (DateTimeField): The date and time when the category was last updated.
    """

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta class for defining metadata options for the Category model.
        """
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def clean(self):
        """
        Cleans the category name by capitalizing it.
        """
        self.category_name = self.category_name.capitalize()

    def __str__(self):
        """
        Returns a string representation of the category.
        """
        return self.category_name


class FoodItem(models.Model):
    """
    Represents a food item in the menu.

    Attributes:
        vendor (Vendor): The vendor associated with the food item.
        category (Category): The category of the food item.
        food_title (str): The title of the food item.
        slug (str): The slug for the food item's URL.
        description (str): The description of the food item.
        price (Decimal): The price of the food item.
        image (ImageField): The image of the food item.
        is_available (bool): Indicates if the food item is available.
        created_at (DateTimeField): The date and time when the food item was created.
        updated_at (DateTimeField): The date and time when the food item was last updated.
    """

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='fooditems')
    food_title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='foodimages')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_title
