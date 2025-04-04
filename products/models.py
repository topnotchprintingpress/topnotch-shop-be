from decimal import Decimal
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

STATUS = {
    ("DT", "Draft"),
    ("PB", "Published"),
}

MAJOR_CATEGORY = {
    ("Books", "Books"),
    ("Technology", "Technology"),
    ("Stationery", "Stationery"),
    ("Lab Equipment", "Lab Equipment")
}


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_category = models.CharField(
        max_length=50, null=True, choices=MAJOR_CATEGORY)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    discount = models.IntegerField(null=True, blank=True)
    featured = models.BooleanField(null=True, default=False, blank=True)
    best_seller = models.BooleanField(null=True, default=False, blank=True)
    status = models.CharField(max_length=2, choices=STATUS, default="DT")
    # For SEO-friendly URLs
    slug = models.SlugField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.title

    def get_discounted_price(self):
        if self.discount and self.discount > 0:
            discount_amount = (Decimal(self.discount) /
                               Decimal(100)) * self.price
            return round(self.price - discount_amount, 2)
        return self.price


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', null=True)


class ProductFeature(models.Model):
    product = models.ForeignKey(
        Product, related_name='features', on_delete=models.CASCADE)
    feature = models.CharField(max_length=250, null=True, blank=True)


class Banner(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banners/')
    link = models.CharField(null=True, max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
