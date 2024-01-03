from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Category)
admin.site.register(ProductRating)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Orderitem)
admin.site.register(ShippingAddress)
admin.site.register(PaymentInfo)