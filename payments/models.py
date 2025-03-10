from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class PaymentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_paid = models.IntegerField()
    reference_code = models.CharField(max_length=100)
    payment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Payment History'

    def __str__(self):
        return f"{self.user.username} - {self.amount_paid} - {self.reference_code}"


class ShippingAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shipping_addresses')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shipping Address for {self.user.username}"

    class Meta:
        verbose_name_plural = 'Shipping Addresses'
