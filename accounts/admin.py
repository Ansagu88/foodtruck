"""
This module contains the admin configuration for the accounts app.

It registers the custom user model and user profile model with the Django admin site.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile


# Register your models here.


class CustomUserAdmin(UserAdmin):
    """
    Admin class for managing custom user model.

    Attributes:
        list_display (tuple): A tuple of field names to be displayed in the admin list view.
        ordering (tuple): A tuple of field names used for ordering the list view.
        filter_horizontal (tuple): A tuple of field names to be displayed
        as horizontal filter options.
        list_filter (tuple): A tuple of field names used for filtering the list view.
        fieldsets (tuple): A tuple of fieldsets to be displayed in the admin form view.
    """

    list_display = ("email", "first_name", "last_name", "username", "role", "is_active")
    ordering = ("-date_joined",)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
