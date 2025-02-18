from rest_framework import viewsets
from .models import Category, Product
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['best_seller']

    def get_queryset(self):
        queryset = self.queryset.filter(status="PB")
        main_category = self.request.query_params.get('main_category', None)

        if main_category:
            queryset = queryset.filter(main_category=main_category)
        return queryset
