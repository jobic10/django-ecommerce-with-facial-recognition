from django.db.models.signals import post_save
from django.contrib.auth.models import User
from store import models


# def create_customer_to_user(sender, instance, created, **kwargs):
#     """
#     Creates customer to each User (One to One relations).
#     :param sender:
#     :param instance:
#     :param created:
#     :param kwargs:
#     :return:
#     """
#     print(kwargs)
#     print(instance)
#     phone = instance.phone
#     if created:
#         models.Customer.objects.create(
#             user=instance,  phone=phone)


# post_save.connect(create_customer_to_user, sender=User)
