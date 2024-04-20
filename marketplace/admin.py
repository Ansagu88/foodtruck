"""
This module contains the admin configuration for the marketplace app.
It regiters the Cart and Tax models with the admin interface.
"""
from django.contrib import admin

from .models import Cart, Tax

class CartAdmin(admin.ModelAdmin):
    """
    Admin class for managing the Cart model in the admin interface.
    """
    list_display = ('user', 'fooditem', 'quantity', 'updated_at')


class TaxAdmin(admin.ModelAdmin):
    """
    Admin class for managing tax settings.

    Attributes:
        list_display (tuple): A tuple of field names to be displayed in the admin list view.
            The fields include 'tax_type', 'tax_percentage', and 'is_active'.
    """
    list_display = ('tax_type', 'tax_percentage', 'is_active')


admin.site.register(Cart, CartAdmin)
admin.site.register(Tax, TaxAdmin)
