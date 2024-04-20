"""
This module contains the admin configuration for the meno app.

It registers the FoodItem model and Category model with the Django admin site.
"""

from django.contrib import admin
from .models import Category, FoodItem


class CategoryAdmin(admin.ModelAdmin):
    """
    Admin class for managing categories in the food truck menu.

    Attributes:
        prepopulated_fields (dict): A dictionary specifying the fields to be prepopulated.
        list_display (tuple): A tuple specifying the fields to be displayed in the list view.
        search_fields (tuple): A tuple specifying the fields to be searched in the admin interface.
    """
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'vendor', 'updated_at')
    search_fields = ('category_name', 'vendor__vendor_name')


class FoodItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for the FoodItem model.

    This class defines the behavior of the admin interface for the FoodItem model.
    It specifies the prepopulated fields, list display, search fields, and list filters.

    Attributes:
        prepopulated_fields (dict): A dictionary specifying the fields to be prepopulated.
        list_display (tuple): A tuple specifying the fields to be displayed in the list view.
        search_fields (tuple): A tuple specifying the fields to be searched in the admin interface.
        list_filter (tuple): A tuple specifying the fields to be used for filtering the list view.
    """

    prepopulated_fields = {'slug': ('food_title',)}
    list_display = ('food_title', 'category', 'vendor', 'price', 'is_available', 'updated_at')
    search_fields = ('food_title', 'category__category_name', 'vendor__vendor_name', 'price')
    list_filter = ('is_available',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
