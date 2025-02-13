from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, BookViewSet, StationeryViewSet, LabEquipmentViewSet, DeviceViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'books', BookViewSet)
router.register(r'stationery', StationeryViewSet)
router.register(r'lab-equipment', LabEquipmentViewSet)
router.register(r'device', DeviceViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
