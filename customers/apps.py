"""
This module represents the configuration for the 'customers' app in the Django project.

"""

from django.apps import AppConfig


class CustomersConfig(AppConfig):
    """
    AppConfig for the 'customers' app.

    This class defines the configuration for the 'customers' app in the Django project.
    It specifies the default auto field and the name of the app.

    Attributes:
        default_auto_field (str): The default auto field to use for models in the app.
        name (str): The name of the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customers'
