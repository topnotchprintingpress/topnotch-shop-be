import requests
import uuid
from django.shortcuts import render, get_object_or_404
from .serializers import ShippingSerializer
from .models import ShippingAddress
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import PaymentHistory
from orders.models import Order, OrderItem
from cart.models import Cart
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import User


class ShippingViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_payment(request):
    data = request.data
    user = request.user
    email = user.email
    amount = float(request.data.get("amount", 0)) * 100

    if amount <= 0:
        return JsonResponse({"status": "error", "message": "Invalid amount"}, status=400)

    cart = Cart.objects.filter(user=user).first()
    if not cart or not cart.items.exists():
        return JsonResponse({"status": "error", "message": "Cart is empty"}, status=400)

    # Store cart details in metadata
    cart_items = [
        {"product": item.product.title, "quantity": item.quantity,
            "price": float(item.product.price)}
        for item in cart.items.all()
    ]

    shipping_address = ShippingAddress.objects.filter(user=user).first()

    if shipping_address:  # Ensure it's not None
        shipping = {
            "first_name": shipping_address.first_name,
            "last_name": shipping_address.last_name,
            "street_address": shipping_address.street_address,
            "apartment": shipping_address.apartment,
            "city": shipping_address.city,
            "county": shipping_address.county,
            "country": shipping_address.country,
            "postal_code": shipping_address.postal_code,
            "phone_number": shipping_address.phone_number,
        }
    else:
        shipping = None  # Handle case where user has no shipping address

    ref = str(uuid.uuid4())

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "amount": amount,
        "metadata": {"user": email, "cart_items": cart_items},
        "shipping_address": shipping,
        "callback_url": "http://localhost:3000/payment/success",
    }
    url = "https://api.paystack.co/transaction/initialize"
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad responses
    except requests.exceptions.RequestException as e:
        return JsonResponse({"status": "error", "message": f"Payment initiation failed: {str(e)}"}, status=500)

    return JsonResponse(response.json())


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def process_payment(request):
    reference = request.data.get("reference")
    if not reference:
        return JsonResponse({'status': 'error', 'message': 'Reference is required'}, status=400)

    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return JsonResponse({'status': 'error', 'message': f"Payment verification failed: {str(e)}"}, status=500)

    response_data = response.json()

    if response_data.get('status') and response_data['data']['status'] == "success":
        user_email = response_data['data']['customer']['email']
        user = get_object_or_404(User, email=user_email)
        amount_paid = response_data['data']['amount'] / 100
        metadata = response_data['data'].get('metadata', {})
        cart_items = metadata.get("cart_items", [])

        if not cart_items:
            return JsonResponse({'status': 'error', 'message': 'No cart data found'}, status=400)

        # Retrieve the user's cart
        cart = Cart.objects.filter(user=user).first()
        if not cart:
            return JsonResponse({'status': 'error', 'message': 'User cart not found'}, status=400)

        # Retrieve shipping address
        shipping_address = ShippingAddress.objects.filter(user=user).first()
        if not shipping_address:
            return JsonResponse({'status': 'error', 'message': 'No shipping address found'}, status=400)

        try:
            # ✅ Create the order only ONCE
            order = Order.objects.create(
                user=user,
                total_price=amount_paid,
                shipping_address=shipping_address
            )

            # ✅ Attach order items properly
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order, product=item.product, quantity=item.quantity, price=item.product.price
                )

            print(f"Order successfully created: {order.id}")

        except Exception as e:
            print(f"Order creation failed: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Order creation failed'}, status=500)

        # ✅ Save payment history
        PaymentHistory.objects.create(
            user=user,
            amount_paid=order.total_price,
            reference_code=reference,
            payment_date=timezone.now()
        )

        # ✅ Clear cart after successful payment
        cart.items.all().delete()
        cart.delete()

        return JsonResponse({'status': 'success', 'message': 'Payment verified, order is processing.'})

    return JsonResponse({'status': 'error', 'message': 'Payment verification failed'}, status=400)
