"""
In this module, we define the user manager, the custom user model and 
the user profile model for the application.
We define they methods and attributes of the models and the manager.

"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.fields.related import OneToOneField

from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point


# Create your models here.
class UserManager(BaseUserManager):
    """
    Custom manager for the User model.

    This manager provides methods to create and manage user objects.

    Attributes:
        _db (str): The database alias to use when saving the user.

    Methods:
        create_user: Creates and saves a new user with the given information.
        create_superuser: Creates a superuser with the given information.
    """

    def create_user(self, first_name, last_name, username, email, password=None):
        """
        Creates and saves a new user with the given information.

        Args:
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
            username (str): The username of the user.
            email (str): The email address of the user.
            password (str, optional): The password for the user. Defaults to None.

        Raises:
            ValueError: If email or username is not provided.

        Returns:
            User: The newly created user object.
        """
        if not email:
            raise ValueError("User must have an email address")

        if not username:
            raise ValueError("User must have an username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        """
        Create a superuser with the given information.

        Args:
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
            username (str): The username of the user.
            email (str): The email address of the user.
            password (str, optional): The password for the user. Defaults to None.

        Returns:
            User: The created superuser.
        """
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    Custom user model representing a user of the application.

    This model extends the AbstractBaseUser class provided by Django
    to create a custom user model with additional fields and methods.

    Attributes:
        VENDOR (int): Constant representing the vendor role.
        CUSTOMER (int): Constant representing the customer role.
        ROLE_CHOICE (tuple): Choices for the role field.
        first_name (CharField): First name of the user.
        last_name (CharField): Last name of the user.
        username (CharField): Username of the user.
        email (EmailField): Email address of the user.
        phone_number (CharField): Phone number of the user.
        role (PositiveSmallIntegerField): Role of the user.
        date_joined (DateTimeField): Date and time when the user joined.
        last_login (DateTimeField): Date and time of the last login.
        created_date (DateTimeField): Date and time when the user was created.
        modified_date (DateTimeField): Date and time of the last modification.
        is_admin (BooleanField): Flag indicating if the user is an admin.
        is_staff (BooleanField): Flag indicating if the user is a staff member.
        is_active (BooleanField): Flag indicating if the user is active.
        is_superadmin (BooleanField): Flag indicating if the user is a superadmin.
        USERNAME_FIELD (str): Field used as the unique identifier for the user.
        REQUIRED_FIELDS (list): List of fields required when creating a user.

    Methods:
        __str__(): Returns a string representation of the user.
        has_perm(perm, obj=None): Checks if the user has a specific permission.
        has_module_perms(app_label): Checks if the user has any permissions in the given app_label.
        get_role(): Returns the role of the user.
    """

    VENDOR = 1
    CUSTOMER = 2

    ROLE_CHOICE = (
        (VENDOR, "Vendor"),
        (CUSTOMER, "Customer"),
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)

    # required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of the user.

        This method is used to provide a human-readable string representation
        of the user when it is converted to a string using the str() function
        or when it is printed.

        Returns:
            str: A string representation of the user.
        """
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Check if the user has a specific permission.

        Args:
            perm (str): The permission to check.
            obj (object, optional): The object to check the permission against. Defaults to None.

        Returns:
            bool: True if the user has the permission, False otherwise.
        """
        return self.is_admin

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app_label.
        """
        return True

    def get_role(self):
        """
        Returns the role of the user.

        Returns:
            str: The role of the user. Possible values are 'Vendor' or 'Customer'.
        """
        if self.role == 1:
            user_role = "Vendor"
        elif self.role == 2:
            user_role = "Customer"
        return user_role


class UserProfile(models.Model):
    """
    Represents a user profile.

    Attributes:
        user (OneToOneField): The associated user.
        profile_picture (ImageField): The profile picture of the user.
        cover_photo (ImageField): The cover photo of the user.
        address (CharField): The address of the user.
        country (CharField): The country of the user.
        state (CharField): The state of the user.
        city (CharField): The city of the user.
        pin_code (CharField): The pin code of the user.
        latitude (CharField): The latitude of the user's location.
        longitude (CharField): The longitude of the user's location.
        location (PointField): The location of the user represented as a point.
        created_at (DateTimeField): The date and time when the user profile was created.
        modified_at (DateTimeField): The date and time when the user profile was last modified.
    """

    user = OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="users/profile_pictures", blank=True, null=True
    )
    cover_photo = models.ImageField(
        upload_to="users/cover_photos", blank=True, null=True
    )
    address = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    location = gismodels.PointField(blank=True, null=True, srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude))
            return super(UserProfile, self).save(*args, **kwargs)
        return super(UserProfile, self).save(*args, **kwargs)


class Subscriber(models.Model):
    """
    Represents a subscriber to the food truck application.

    Attributes:
        email (str): The email address of the subscriber.
    """

    email = models.EmailField(unique=True)

    def __str__(self):
        """
        Returns a string representation of the object.

        This method is used to provide a human-readable string representation
        of the object when it is converted to a string using the str() function
        or when it is printed.

        Returns:
            str: A string representation of the object.
        """
        return self.email
