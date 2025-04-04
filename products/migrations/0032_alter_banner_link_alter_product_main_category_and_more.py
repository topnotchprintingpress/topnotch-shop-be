# Generated by Django 5.1.5 on 2025-03-24 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0031_remove_banner_position_alter_product_main_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='link',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='main_category',
            field=models.CharField(choices=[('Lab Equipment', 'Lab Equipment'), ('Books', 'Books'), ('Technology', 'Technology'), ('Stationery', 'Stationery')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('PB', 'Published'), ('DT', 'Draft')], default='DT', max_length=2),
        ),
    ]
