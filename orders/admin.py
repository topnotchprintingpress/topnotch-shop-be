from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No extra empty rows
    readonly_fields = ('price',)
    # Price should not be editable after creation


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'id')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product_name', 'quantity', 'price')
    list_filter = ('order__status',)

    def product_name(self, obj):
        if obj.book:
            return obj.book.title
        elif obj.stationery:
            return obj.stationery.name
        elif obj.lab_equipment:
            return obj.lab_equipment.name
        return "Unknown Product"
    product_name.short_description = 'Product'
