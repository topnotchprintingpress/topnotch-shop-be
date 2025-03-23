import os
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
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet


class ShippingViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        shipping = self.get_object()
        serializer = self.get_serializer(
            shipping, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_payment(request):
    user = request.user
    email = user.email

    cart = Cart.objects.filter(user=user).first()
    if not cart or not cart.items.exists():
        return JsonResponse({"status": "error", "message": "Cart is empty"}, status=400)

    # Apply discounts and calculate the correct amount
    cart_items = [
        {
            "product": item.product.title,
            "quantity": item.quantity,
            "original_price": float(item.product.price),
            "discounted_price": float(item.product.get_discounted_price()),
        }
        for item in cart.items.all()
    ]

    # Correct total amount with discounts applied
    amount = sum(
        item["quantity"] * item["discounted_price"]
        for item in cart_items
    ) * 100  # Convert to cents for Paystack

    if amount <= 0:
        return JsonResponse({"status": "error", "message": "Invalid amount"}, status=400)

    shipping_address = ShippingAddress.objects.filter(user=user).first()
    shipping = None
    if shipping_address:
        shipping = {
            "first_name": shipping_address.first_name,
            "last_name": shipping_address.last_name,
            "email": shipping_address.email,
            "street_address": shipping_address.street_address,
            "apartment": shipping_address.apartment,
            "city": shipping_address.city,
            "county": shipping_address.county,
            "country": shipping_address.country,
            "postal_code": shipping_address.postal_code,
            "phone_number": shipping_address.phone_number,
        }

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
            total_price = sum(
                item.quantity * item.product.get_discounted_price()
                for item in cart.items.all()
            )
            # Create the order only ONCE
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                shipping_address=shipping_address,
                order_reference=reference,
                status="PROCESSING"

            )

            # Attach order items properly
            for item in cart.items.all():
                discounted_price = item.product.get_discounted_price()
                OrderItem.objects.create(
                    order=order, product=item.product, quantity=item.quantity, price=discounted_price
                )

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Order creation failed'}, status=500)

        # Save payment history
        PaymentHistory.objects.create(
            user=user,
            amount_paid=order.total_price,
            reference_code=reference,
            payment_date=timezone.now()
        )

        # Clear cart after successful payment
        cart.items.all().delete()
        cart.delete()

        return JsonResponse({'status': 'success', 'message': 'Payment verified, order is processing.'})

    return JsonResponse({'status': 'error', 'message': 'Payment verification failed'}, status=400)


def generate_invoice(request, order_id, order_reference):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=404)

    customer_name = f"{order.shipping_address.first_name}{order.shipping_address.last_name}".replace(
        " ", "")
    order_date = order.created_at.strftime("%Y%m%d")
    file_name = f"Invoice_{order_reference}_{customer_name}_{order_date}.pdf"

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'

    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # === BRAND COLORS ===
    PAGE_BG_COLOR = "#FFFCF7"  # Light cream background
    HEADER_BG_COLOR = "#2B0909"  # Dark maroon for headers

    # === ADD COMPANY LOGO ===
    try:
        # Path to the logo in your static folder
        logo_path = os.path.join(
            settings.BASE_DIR, 'products', 'static', 'products', 'images', 'Logo1.png')
        logo = Image(logo_path, width=2 * inch, height=1 * inch)
        elements.append(logo)
    except Exception:
        # Fallback if logo is missing
        elements.append(Paragraph("<b>Company Name</b>", styles["Title"]))

    elements.append(Spacer(1, 0.2 * inch))

    # === INVOICE TITLE ===
    elements.append(
        Paragraph(f"Invoice for Order Reference No: {order.order_reference}", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    # === CUSTOMER & ORDER DETAILS ===
    customer_info = f"""
    <b>Order Date:</b> {order.created_at.strftime('%Y-%m-%d %H:%M')}<br/>
    <b>Customer:</b> {order.shipping_address.first_name} {order.shipping_address.last_name}<br/>
    <b>Address:</b> {order.shipping_address.street_address}, {order.shipping_address.city}, {order.shipping_address.country}<br/>
    <b>Phone:</b> {order.shipping_address.phone_number if order.shipping_address.phone_number else 'N/A'}<br/>
    """
    elements.append(Paragraph(customer_info, styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # === TABLE HEADER ===
    data = [["Item", "Quantity", "Unit Price (KES)", "Total (KES)"]]

    # === ADD ORDER ITEMS ===
    for item in order.items.all():
        product_title = Paragraph(
            item.product.title, styles["Normal"])  # Wrap text
        quantity = item.quantity
        price = f"{item.product.get_discounted_price():,.2f}"  # Format price
        # Calculate subtotal
        subtotal = f"{item.quantity * item.product.get_discounted_price():,.2f}"

        data.append([product_title, quantity, price, subtotal])

    # === ADD TOTAL ROW ===
    data.append(["", "", Paragraph("<b>Grand Total:</b>", styles["Normal"]),
                Paragraph(f"<b>{order.total_price:,.2f} KES</b>", styles["Normal"])])

    # === CREATE STYLED TABLE ===
    table = Table(data, colWidths=[3 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor(HEADER_BG_COLOR)),  # Header color
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),  # White text in header
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        # Light beige for Grand Total row
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DDD2C0")),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    # === FOOTER NOTE ===
    elements.append(
        Paragraph("<i>Thank you for shopping with us!</i>", styles["Italic"]))

    # === BUILD PDF ===
    doc.build(elements)
    return response
