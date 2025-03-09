from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cart
from users.models import User  # Import your User model

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:  # If a new user is created
        Cart.objects.create(user=instance)
