from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from .models import Order, Product

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=Order)
def reduce_stock_on_order(sender, instance, created, **kwargs):
    if created:  # Ensure this only runs when a new order is created
        product = instance.product
        if product.stock_quantity >= instance.quantity:
            product.stock_quantity -= instance.quantity
            product.save()
            print("Signal triggered for order creation.")

        else:
            # Handle unexpected case: insufficient stock
            #raise ValueError("Insufficient stock for this order")
            print("Insufficient stock for this order.")