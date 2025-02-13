from django.db import models

STATUS = {
    "DT": "Draft",
    "PB": "Published",
}


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='books')
    stock = models.PositiveIntegerField(default=0)
    discount = models.IntegerField(null=True, blank=True)
    featured = models.BooleanField(null=True, default=False, blank=True)
    status = models.CharField(max_length=2, choices=STATUS, default="DT")
    # For SEO-friendly URLs
    slug = models.SlugField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.title


class BookImage(models.Model):
    book = models.ForeignKey(
        Book, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='books/', null=True)


class Stationery(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='stationery')
    stock = models.PositiveIntegerField(default=0)
    discount = models.IntegerField(null=True, blank=True)
    featured = models.BooleanField(null=True, default=False, blank=True)
    status = models.CharField(max_length=2, choices=STATUS, default="DT")
    slug = models.SlugField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Stationery'

    def __str__(self):
        return self.name


class StationeryImage(models.Model):
    stationery = models.ForeignKey(
        Stationery, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='stationery/', null=True)


class LabEquipment(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='lab_equipment')
    stock = models.PositiveIntegerField(default=0)
    discount = models.IntegerField(null=True, blank=True)
    featured = models.BooleanField(null=True, default=False, blank=True)
    status = models.CharField(max_length=2, choices=STATUS, default="DT")
    slug = models.SlugField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Lab Equipment'

    def __str__(self):
        return self.name


class LabImage(models.Model):
    laboratory = models.ForeignKey(
        LabEquipment, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='laboratory/', null=True)


class Device(models.Model):
    name = models.CharField(max_length=250, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='devices')
    stock = models.PositiveIntegerField(default=0)
    discount = models.IntegerField(null=True, blank=True)
    featured = models.BooleanField(null=True, default=False, blank=True)
    status = models.CharField(max_length=2, choices=STATUS, default="DT")
    slug = models.SlugField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Devices'

    def __str__(self):
        return self.name


class DeviceImage(models.Model):
    device = models.ForeignKey(
        Device, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='devices/', null=True)


class DeviceFeature(models.Model):
    device = models.ForeignKey(
        Device, related_name='features', on_delete=models.CASCADE)
    feature = models.CharField(max_length=250, null=True)
