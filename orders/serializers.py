from rest_framework import serializers
from .models import Order, OrderItem
from payments.serializers import ShippingSerializer
from products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'price', 'product']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
