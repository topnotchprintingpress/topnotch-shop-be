from django.contrib import admin
from .models import Category, Book, BookImage, Stationery, StationeryImage, LabEquipment, LabImage, Device, DeviceImage, DeviceFeature


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 2


class StationeryImageInline(admin.TabularInline):
    model = StationeryImage
    extra = 2


class LabImageInline(admin.TabularInline):
    model = LabImage
    extra = 2


class DeviceImageInline(admin.TabularInline):
    model = DeviceImage
    extra = 3


class DeviceFeatureInline(admin.TabularInline):
    model = DeviceFeature
    extra = 5


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'stock')
    list_filter = ('category',)
    inlines = [BookImageInline]
    search_fields = ('title', 'author')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Stationery)
class StationeryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    inlines = [StationeryImageInline]
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(StationeryImage)
class StationeryImageAdmin(admin.ModelAdmin):
    pass


@admin.register(LabEquipment)
class LabEquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    inlines = [LabImageInline]
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(LabImage)
class LabImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('name',)
    inlines = [DeviceImageInline, DeviceFeatureInline]
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(DeviceImage)
class DeviceImageAdmin(admin.ModelAdmin):
    pass


@admin.register(DeviceFeature)
class DeviceFeatureAdmin(admin.ModelAdmin):
    pass
