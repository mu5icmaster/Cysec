from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    def __str__(self): return self.user.get_username()

class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=500, blank=True)
    price_cents = models.PositiveIntegerField()
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    def __str__(self): return self.name

class Order(models.Model):
    STATUS = [("PENDING","Pending"),("CONFIRMED","Confirmed"),("DELIVERED","Delivered")]
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default="PENDING")

class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)
    price_cents = models.PositiveIntegerField()
