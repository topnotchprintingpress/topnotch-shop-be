from rest_framework import serializers
from .models import Category, Book, Stationery, LabEquipment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class StationerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Stationery
        fields = '__all__'


class LabEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabEquipment
        fields = '__all__'
