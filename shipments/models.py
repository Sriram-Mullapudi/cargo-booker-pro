from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import random
import string


def generate_tracking_number():
    """Generate a unique tracking number like CBP1A2B3C4D"""
    prefix = 'CBP'
    chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"{prefix}{chars}"


class Shipment(models.Model):
    CARGO_TYPE_CHOICES = [
        ('documents', 'Documents'),
        ('fragile', 'Fragile Items'),
        ('perishable', 'Perishable Goods'),
        ('electronics', 'Electronics'),
        ('furniture', 'Furniture'),
        ('machinery', 'Machinery'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('booked', 'Booked'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    # User info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipments')
    
    # Tracking
    tracking_number = models.CharField(max_length=20, unique=True, default=generate_tracking_number)
    
    # Sender info
    sender_name = models.CharField(max_length=255)
    sender_email = models.EmailField()
    sender_phone = models.CharField(max_length=20)
    sender_address = models.TextField()
    sender_city = models.CharField(max_length=100)
    sender_postal = models.CharField(max_length=20)
    
    # Receiver info
    receiver_name = models.CharField(max_length=255)
    receiver_email = models.EmailField()
    receiver_phone = models.CharField(max_length=20)
    receiver_address = models.TextField()
    receiver_city = models.CharField(max_length=100)
    receiver_postal = models.CharField(max_length=20)
    
    # Cargo info
    cargo_type = models.CharField(max_length=20, choices=CARGO_TYPE_CHOICES)
    cargo_description = models.TextField()
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Pricing
    cargo_type_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # per kg
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tracking_number} - {self.sender_name} → {self.receiver_name}"
    
    def calculate_price(self):
        """Calculate total price based on cargo type and weight"""
        cargo_prices = {
            'documents': 5,
            'fragile': 15,
            'perishable': 20,
            'electronics': 25,
            'furniture': 30,
            'machinery': 50,
            'other': 10,
        }
        price_per_kg = cargo_prices.get(self.cargo_type, 10)
        self.cargo_type_price = price_per_kg
        self.total_price = float(price_per_kg) * float(self.weight_kg)
        return self.total_price


class StatusUpdate(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='status_updates')
    status = models.CharField(max_length=20, choices=Shipment.STATUS_CHOICES)
    message = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status}"
