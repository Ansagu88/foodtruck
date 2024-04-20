"""
Here we define the models for the vendor app.

"""
from datetime import time, date, datetime
from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification


class Vendor(models.Model):
    """
    Represents a vendor in the food truck marketplace.

    Attributes:
        user (OneToOneField): The user associated with the vendor.
        user_profile (OneToOneField): The user profile associated with the vendor.
        vendor_name (CharField): The name of the vendor.
        vendor_slug (SlugField): The slug field for the vendor's URL.
        vendor_license (ImageField): The image field for the vendor's license.
        is_approved (BooleanField): Indicates if the vendor is approved or not.
        created_at (DateTimeField): The date and time when the vendor was created.
        modified_at (DateTimeField): The date and time when the vendor was last modified.
    """

    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name="userprofile", on_delete=models.CASCADE
    )
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to="vendor/license")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns a string representation of the vendor.

        Returns:
            str: The vendor name.
        """
        return self.vendor_name

    def is_open(self):
        """
        Check if the vendor is currently open.

        Returns:
            bool: True if the vendor is open, False otherwise.
        """
        # Check current day's opening hours.
        today_date = date.today()
        today = today_date.isoweekday()
        current_opening_hours = OpeningHour.objects.filter(vendor=self, day=today)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        is_open = None
        for i in current_opening_hours:
            if not i.is_closed:
                start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
                end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())
                if current_time > start and current_time < end:
                    is_open = True
                    break
                else:
                    is_open = False
        return is_open

    def save(self, *args, **kwargs):
        """
        Save the Vendor object.

        This method overrides the default save method of the Vendor model.
        It performs additional actions when saving the object, such as sending
        notification emails based on the approval status.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            The saved Vendor object.

        Raises:
            Does not raise any exceptions.
        """
        if self.pk is not None:
            # Update
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = "accounts/emails/admin_approval_email.html"
                context = {
                    "user": self.user,
                    "is_approved": self.is_approved,
                    "to_email": self.user.email,
                }
                if self.is_approved is True:
                    # Send notification email
                    mail_subject = "Congratulations! Your restaurant has been approved."
                    send_notification(mail_subject, mail_template, context)
                else:
                    # Send notification email
                    mail_subject = "We're sorry! You are not eligible for publishing your food menu on our marketplace."
                    send_notification(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)


DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]

HOUR_OF_DAY_24 = [
    (time(h, m).strftime("%I:%M %p"), time(h, m).strftime("%I:%M %p"))
    for h in range(0, 24)
    for m in (0, 30)
]


class OpeningHour(models.Model):
    """
    Represents the opening hours for a vendor.

    Attributes:
        vendor (ForeignKey): The vendor associated with the opening hours.
        day (IntegerField): The day of the week for the opening hours.
        from_hour (CharField): The starting hour of the opening hours.
        to_hour (CharField): The ending hour of the opening hours.
        is_closed (BooleanField): Indicates if the vendor is closed for the day.
    """

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        """
        This class defines the metadata options for the Vendor model.

        Attributes:
            ordering (tuple): Specifies the default ordering for the model's records.
                The records will be ordered by the 'day' field in ascending order,
                and then by the 'from_hour' field in descending order.
            unique_together (tuple): Specifies the fields that should be unique together.
                In this case, the combination of 'vendor', 'day', 'from_hour', and 'to_hour'
                should be unique for each record.
        """

        ordering = ("day", "-from_hour")
        unique_together = ("vendor", "day", "from_hour", "to_hour")

    def __str__(self):
        return self.get_day_display()
