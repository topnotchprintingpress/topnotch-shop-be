import requests
import uuid
from django.shortcuts import render
from .serializers import ShippingSerializer
from .models import ShippingAddress
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import PaymentHistory
from orders.models import Order
from cart.models import Cart
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings


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
    amount = float(request.data.get("amount", 0))

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

    ref = str(uuid.uuid4())

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "amount": amount,
        "metadata": {"user": email, "reference": ref, "cart_items": cart_items},
        "callback_url": "http://localhost:3000/payment/success",
    }
    url = "https://api.paystack.co/transaction/initialize"
    response = requests.post(url, headers=headers, json=payload)

    return JsonResponse(response.json())


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def process_payment(request):
    """Verify Paystack payment and update order status."""
    reference = request.data.get("reference")
    if not reference:
        return JsonResponse({'status': 'error', 'message': 'Reference is required'}, status=400)

    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    response = requests.get(url, headers=headers)
    response_data = response.json()

    if response_data.get('status') and response_data['data']['status'] == "success":
        user_email = response_data['data']['customer']['email']
        user = get_object_or_404(User, email=user_email)
        # Convert from kobo
        amount_paid = response_data['data']['amount'] / 100
        cart_items = response_data['data']['metadata'].get("cart_items", [])

        if not cart_items:
            return JsonResponse({'status': 'error', 'message': 'No cart data found'}, status=400)

        order = Order.objects.create(
            user=user, total_price=amount_paid, status="PROCESSING")

        # Save cart items in the order (assuming Order has an `items` field)
        for item in cart_items:
            order.items.create(
                product_name=item["product"],
                quantity=item["quantity"],
                price=item["price"],
            )

        # Save payment history
        PaymentHistory.objects.create(
            user=user,
            amount_paid=order.total_price,
            reference_code=reference,
            payment_date=timezone.now()
        )

        # order.status = "PROCESSING"
        # order.save()

        cart = Cart.objects.filter(user=user).first()
        if cart:
            cart.items.all().delete()
            cart.delete()

    return JsonResponse({'status': 'success', 'message': 'Payment verified, order is processing.'})

    return JsonResponse({'status': 'error', 'message': 'Payment verification failed'}, status=400)
