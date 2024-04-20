"""
This module represents the configuration for the 'accounts' app in the Django project.

"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    AppConfig for the 'accounts' app.

    This class represents the configuration for the 'accounts' app in the Django project.
    It sets the default auto field to 'django.db.models.BigAutoField' and defines a 'ready' method
    to import the signals module from the 'accounts' app.

    Attributes:
        default_auto_field (str): The default auto field for the app.
        name (str): The name of the app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        """
        Method called when the Django project is initialized.

        This method imports the signals module from the 'accounts' app.
        """
        import accounts.signals
