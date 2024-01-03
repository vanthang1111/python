# Generated by Django 4.2.4 on 2023-10-23 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_order_customer_alter_shippingadress_customer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_sub', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=200, null=True)),
                ('slug', models.SlugField(max_length=200, null=True)),
                ('sub_cayegory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_category', to='app.category')),
            ],
        ),
    ]