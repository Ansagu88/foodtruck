"""
This module contains the admin configuration for the 'orders' app.

It registers the OrderedFood model and Order model with the Django admin site.
"""

from django.contrib import admin
from .models import Payment, Order, OrderedFood


class OrderedFoodInline(admin.TabularInline):
    """
    Represents an inline admin view for ordered food items.

    This class is used to display ordered food items in a tabular format
    within the admin interface.

    Attributes:
        model (Model): The model class representing the ordered food item.
        readonly_fields (tuple): A tuple of fields that should be displayed as read-only.
        extra (int): The number of empty forms to display for adding new items.

    """
    model = OrderedFood
    readonly_fields = ('order', 'payment', 'user', 'fooditem', 'quantity', 'price', 'amount')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    """
    Admin class for managing orders.
    """
    list_display = ['order_number', 'name', 'phone', 'email', 'total', 'payment_method', 'status', 'order_placed_to', 'is_ordered']
    inlines = [OrderedFoodInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood)
