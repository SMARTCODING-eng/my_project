from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='profile_picture', unique=True, null=True)
    USER_ROLES = [
        ('admin', 'Admin'),
        ('store_keeper', 'Store_Keeper'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=20,choices=USER_ROLES, default='user')
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        related_name='user_groups',
        blank=True,
        related_query_name="user"
    )
    user_permissions = models.ManyToManyField(
        'auth.permission',
        verbose_name='user permission',
        blank=True,
        related_name="custom_user_set",
        related_query_name="user",
    )

    class Meta:
        swappable = 'AUTH_USER_MODEL'



class Product(models.Model):
    name = models.CharField()
    Description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    Category = models.CharField(max_length=30)
    stock_quantity = models.IntegerField()
    Image_Url = models.URLField(max_length=200, blank=True)
    Created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity =models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
