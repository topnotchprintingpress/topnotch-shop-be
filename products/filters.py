import django_filters
from django.db.models import F, ExpressionWrapper, DecimalField, Value
from django.db.models.functions import Coalesce

from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_price = django_filters.NumberFilter(method='filter_max_price')
    main_category = django_filters.CharFilter(
        field_name="main_category", lookup_expr='icontains'
    )

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'main_category']

    def filter_min_price(self, queryset, name, value):
        return queryset.annotate(
            final_price=ExpressionWrapper(
                F('price') - Coalesce(F('price') * F('discount') / 100, Value(0)),
                output_field=DecimalField()
            )
        ).filter(final_price__gte=value)

    def filter_max_price(self, queryset, name, value):
        return queryset.annotate(
            final_price=ExpressionWrapper(
                F('price') - Coalesce(F('price') * F('discount') / 100, Value(0)),
                output_field=DecimalField()
            )
        ).filter(final_price__lte=value)
