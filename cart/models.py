from django.db import models
from django.conf import settings
from products.models import Book, Stationery, LabEquipment
from django.contrib.auth.models import User


class Cart(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, null=True, blank=True)
    stationery = models.ForeignKey(
        Stationery, on_delete=models.CASCADE, null=True, blank=True)
    lab_equipment = models.ForeignKey(
        LabEquipment, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        if self.book:
            return f"{self.quantity}x {self.book.title} in Cart"
        elif self.stationery:
            return f"{self.quantity}x {self.stationery.name} in Cart"
        elif self.lab_equipment:
            return f"{self.quantity}x {self.lab_equipment.name} in Cart"
        else:
            return "Item in Cart"

    @property
    def total_price(self):
        if self.book:
            return self.quantity * self.book.price
        elif self.stationery:
            return self.quantity * self.stationery.price
        elif self.lab_equipment:
            return self.quantity * self.lab_equipment.price
        return 0
