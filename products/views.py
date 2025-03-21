from rest_framework import viewsets
from .models import Category, Product, Banner
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CategorySerializer, ProductSerializer, BannerSerializer
from django.db.models import Q
from .filters import ProductFilter


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['best_seller', 'slug']

    def get_queryset(self):
        queryset = Product.objects.filter(status="PB").order_by('-created_at')
        main_category = self.request.query_params.get('main_category', None)
        search_query = self.request.query_params.get('search')

        if main_category:
            queryset = queryset.filter(main_category=main_category)

        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(
                description__icontains=search_query))
        return queryset


class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

    def get_queryset(self):
        position = self.request.query_params.get('position', None)
        queryset = self.queryset.filter(is_active=True)
        if position:
            queryset = self.queryset.filter(position=position)
        return queryset
