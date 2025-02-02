from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from products.models import Book, Stationery, LabEquipment


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(
        Book, on_delete=models.SET_NULL, null=True, blank=True)
    stationery = models.ForeignKey(
        Stationery, on_delete=models.SET_NULL, null=True, blank=True)
    lab_equipment = models.ForeignKey(
        LabEquipment, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    # Price at the time of purchase
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        if self.book:
            return f"{self.quantity}x {self.book.title} in Order #{self.order.id}"
        elif self.stationery:
            return f"{self.quantity}x {self.stationery.name} in Order #{self.order.id}"
        elif self.lab_equipment:
            return f"{self.quantity}x {self.lab_equipment.name} in Order #{self.order.id}"
        else:
            return f"Item in Order #{self.order.id}"
