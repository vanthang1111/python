# Generated by Django 4.1.7 on 2023-12-22 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_rename_shippingadress_shippingaddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='purchase_count',
            field=models.IntegerField(default=0),
        ),
    ]
