from django.contrib import admin
from .models import Category, Product, ProductImage, ProductFeature, Banner


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


class ProductFeatureInline(admin.StackedInline):
    model = ProductFeature
    extra = 5


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'stock')
    list_filter = ('category',)
    inlines = [ProductImageInline]
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductFeature)
class ProductFeatureAdmin(admin.ModelAdmin):
    pass


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'is_active')
