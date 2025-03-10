from rest_framework import viewsets
from .models import Order
from payments.models import ShippingAddress
from .serializers import OrderSerializer
from rest_framework.decorators import action
from payments.serializers import ShippingSerializer
from cart.models import Cart


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Only allow users to view their own orders
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        """Convert cart items into an order and empty the cart."""
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # get shipping address
        shipping_address = ShippingAddress.objects.filter(user=user).first()
        if not shipping_address:
            return Response({"error": "Shipping address required"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.product.price *
                          item.quantity for item in cart.items.all())

        order = Order.objects.create(
            user=user, total_price=total_price, shipping_address=shipping_address)

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order, product=item.product, quantity=item.quantity, price=item.product.price)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
