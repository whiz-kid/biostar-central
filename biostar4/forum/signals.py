from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from biostar4.forum.models import *
from . import utils

@receiver(pre_save, sender=User)
def set_username(sender, instance, **kwargs):
    """
    Creates a username for the user.
    """
    # We need this to avoid race conditions during user signup.
    instance.username = instance.username or utils.get_uuid()
    print (instance.id, instance.email)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Creates profile on user save. Also updates the
    usename field based on a database id.
    """
    if created:
        # Set default name
        name = instance.email.split('@')[0]
        Profile.objects.create(user=instance, name=name)
        # Since we only ask for email we'll make a nicer username.
        User.objects.filter(id=instance.id).update(username='user%d' % instance.id)