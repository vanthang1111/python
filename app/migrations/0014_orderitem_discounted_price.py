# Generated by Django 4.2.4 on 2023-11-22 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_product_discount_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='discounted_price',
            field=models.FloatField(default=0),
        ),
    ]
