from django.contrib import admin
from .models import PaymentHistory, ShippingAddress


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_paid', 'reference_code', 'payment_date')
    search_fields = ('user__username', 'reference_code')
    list_filter = ('payment_date',)
    readonly_fields = ('payment_date',)


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name',
                    'last_name', 'city', 'created_at')
    search_fields = ('user__username', 'city', 'postal_code')
    list_filter = ('country', 'city', 'created_at')
    readonly_fields = ('created_at',)
