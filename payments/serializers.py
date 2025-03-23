from rest_framework import serializers
from .models import ShippingAddress


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ["id", "first_name", "last_name", "email", "street_address", "apartment",
                  "city", "county", "country", "postal_code", "phone_number"]
