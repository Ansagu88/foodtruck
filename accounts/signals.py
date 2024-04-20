"""
In this module we define the signal receivers for the User model. 
We use the `@receiver` decorator to connect the signal
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    """
    Signal receiver function that creates a user profile after saving a user instance.

    Args:
        sender: The model class that sent the signal.
        instance: The actual instance being saved.
        created: A boolean value indicating whether the instance was created or not.
        kwargs: Additional keyword arguments.

    Returns:
        None
    """
    print(created)
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # Create the userprofile if not exist
            UserProfile.objects.create(user=instance)


@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    """
    This is a pre-save signal receiver function for the User model.
    It is triggered before saving a User instance.
    """
    pass


# post_save.connect(post_save_create_profile_receiver, sender=User)
