from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_picture', unique=True, null=True)
    USER_ROLES = [
        ('owner', 'Owner'),
        ('store manager', 'Store manager'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(max_length=20,choices=USER_ROLES, default='customer')
    profile_picture = models.ImageField(upload_to='profile_pictures/')

    class Meta:
        swappable = 'AUTH_USER_MODEL'


