# Generated by Django 4.1.7 on 2023-12-23 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_remove_product_purchase_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='purchase_count',
            field=models.IntegerField(default=0),
        ),
    ]
