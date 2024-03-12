from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)

    groups = models.ManyToManyField('auth.Group', related_name='customuser_groups')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_user_permissions')

    def __str__(self):
        return self.username

