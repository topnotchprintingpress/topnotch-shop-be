from rest_framework import viewsets
from .models import Category, Product, Banner
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CategorySerializer, ProductSerializer, BannerSerializer
from django.db.models import Q
from .filters import ProductFilter
from django.db.models import F, ExpressionWrapper, DecimalField, Value
from django.db.models.functions import Coalesce


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['best_seller', 'slug', 'main_category', 'discount']

    def get_queryset(self):
        queryset = Product.objects.filter(status="PB").order_by()
        slug = self.request.query_params.get("slug", None)
        if slug:
            filtered_queryset = queryset.filter(slug__iexact=slug)
            # Debugging: Log the generated SQL query
            print(filtered_queryset.query)

            if not filtered_queryset.exists():
                return filtered_queryset.none()  # Return an empty queryset
            return filtered_queryset
        main_category = self.request.query_params.get('main_category', None)
        search_query = self.request.query_params.get('search')
        min_price = self.request.query_params.get("min_price", None)
        max_price = self.request.query_params.get("max_price", None)
        is_best_seller = self.request.query_params.get("is_best_seller", None)
        is_new_arrival = self.request.query_params.get("is_new_arrival", None)
        is_discounted = self.request.query_params.get("is_discounted", None)

        # If is_new_arrival is set, return all products ordered by created_at (ignore filters)
        if is_new_arrival:
            return queryset

        # Apply filters normally when is_new_arrival is not set
        if main_category:
            queryset = queryset.filter(main_category__iexact=main_category)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(
                    description__icontains=search_query)
            )

        if is_best_seller:
            queryset = queryset.filter(best_seller=True)

        if is_discounted:
            queryset = queryset.filter(discount__gt=0)

        queryset = queryset.annotate(
            final_price=ExpressionWrapper(
                F('price') - Coalesce(F('price') * F('discount') / 100, Value(0)),
                output_field=DecimalField()
            )
        )

        # Convert price filters to numbers before using them
        try:
            if min_price is not None:
                min_price = float(min_price)
                queryset = queryset.filter(final_price__gte=min_price)

            if max_price is not None:
                max_price = float(max_price)
                queryset = queryset.filter(final_price__lte=max_price)

        except ValueError:
            print("Invalid min_price or max_price value received")  # Debugging

        return queryset


class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    pagination_class = None

    def get_queryset(self):
        position = self.request.query_params.get('position', None)
        queryset = self.queryset.filter(is_active=True)
        if position:
            queryset = self.queryset.filter(position=position)
        return queryset
