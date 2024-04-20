"""
This module represents the configuration for the 'menu' app in the Django project.

"""

from django.apps import AppConfig


class MenuConfig(AppConfig):
    """
    AppConfig for the 'menu' app.

    This class represents the configuration for the 'menu' app in the Django project.
    It sets the default auto field to 'django.db.models.BigAutoField' and specifies the name of the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'menu'
