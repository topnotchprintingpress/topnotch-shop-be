from rest_framework import serializers
from .models import Category, Book, BookImage, Stationery, StationeryImage, LabEquipment, LabImage, Device, DeviceImage, DeviceFeature


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    images = BookImageSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = '__all__'


class StationeryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationeryImage
        fields = '__all__'


class StationerySerializer(serializers.ModelSerializer):
    images = StationeryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Stationery
        fields = '__all__'


class LabImageSerializer(serializers.ModelSerializer):
    class Meta:
        models = LabImage
        fields = '__all__'


class LabEquipmentSerializer(serializers.ModelSerializer):
    images = LabImageSerializer(many=True, read_only=True)

    class Meta:
        model = LabEquipment
        fields = '__all__'


class DeviceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceImage
        fields = '__all__'


class DeviceFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceFeature
        fields = '__all__'


class DeviceListSerializer(serializers.ModelSerializer):
    images = DeviceImageSerializer(many=True)
    features = DeviceFeatureSerializer(many=True)

    class Meta:
        model = Device
        fields = '__all__'
