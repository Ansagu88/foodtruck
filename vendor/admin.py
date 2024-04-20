"""
This module contains the admin configuration for the vendor app.

It registers the Vendor model and Opening Hour model with the Django admin site.
"""

from django.contrib import admin
from vendor.models import Vendor, OpeningHour


class VendorAdmin(admin.ModelAdmin):
    """
    Admin class for managing vendors.
    """

    list_display = ("user", "vendor_name", "is_approved", "created_at")
    list_display_links = ("user", "vendor_name")
    list_editable = ("is_approved",)


class OpeningHourAdmin(admin.ModelAdmin):
    """
    Admin class for managing opening hours of vendors.
    """

    list_display = ("vendor", "day", "from_hour", "to_hour")


admin.site.register(Vendor, VendorAdmin)
admin.site.register(OpeningHour, OpeningHourAdmin)
