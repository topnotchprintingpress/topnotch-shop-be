from rest_framework import viewsets
from .models import Category, Book, Stationery, LabEquipment
from .serializers import CategorySerializer, BookSerializer, StationerySerializer, LabEquipmentSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class StationeryViewSet(viewsets.ModelViewSet):
    queryset = Stationery.objects.all()
    serializer_class = StationerySerializer


class LabEquipmentViewSet(viewsets.ModelViewSet):
    queryset = LabEquipment.objects.all()
    serializer_class = LabEquipmentSerializer
