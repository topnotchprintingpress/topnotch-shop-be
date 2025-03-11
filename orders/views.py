from rest_framework import viewsets
from .models import Order, OrderItem
from payments.models import ShippingAddress
from .serializers import OrderSerializer
from rest_framework.decorators import action
from payments.serializers import ShippingSerializer
from cart.models import Cart
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import User


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Only allow users to view their own orders
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
