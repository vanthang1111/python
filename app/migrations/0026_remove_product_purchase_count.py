# Generated by Django 4.1.7 on 2023-12-22 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_product_purchase_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='purchase_count',
        ),
    ]
