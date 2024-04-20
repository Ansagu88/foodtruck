"""
In this module we created the models Cart and Tax. 
The Cart model represents a cart item in the marketplace, 
and the Tax model represents a tax entity in the marketplace. 

"""

from django.db import models

from accounts.models import User
from menu.models import FoodItem


class Cart(models.Model):
    """
    Represents a cart item in the marketplace.

    Attributes:
        user (User): The user who owns the cart.
        fooditem (FoodItem): The food item added to the cart.
        quantity (int): The quantity of the food item in the cart.
        created_at (datetime): The date and time when the cart item was created.
        updated_at (datetime): The date and time when the cart item was last updated.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user


class Tax(models.Model):
    """
    Represents a tax entity in the marketplace.
    """

    tax_type = models.CharField(max_length=20, unique=True)
    tax_percentage = models.DecimalField(
        decimal_places=2, max_digits=4, verbose_name="Tax Percentage (%)"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        """
        This class provides options for the model's metadata.
        """
        verbose_name_plural = "tax"

    def __str__(self):
        return self.tax_type
