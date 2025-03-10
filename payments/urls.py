from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShippingViewSet
from . import views

router = DefaultRouter()
router.register(r'shipping', ShippingViewSet)

urlpatterns = [
    path('submit/', views.submit_payment, name='submit_payment'),
    path('process_payment/', views.process_payment, name='process_payment'),
]
