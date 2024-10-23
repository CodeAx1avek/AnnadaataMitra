from django.db import models
from django.contrib.auth.models import User

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    state = models.CharField(max_length=50, default="")
    district = models.CharField(max_length=50, default="")
    city = models.CharField(max_length=50, default="")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    interests = models.TextField()

    def __str__(self):
        return self.name

class Product(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    quality = models.CharField(max_length=50)  # Adjust max_length as needed
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='product/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
