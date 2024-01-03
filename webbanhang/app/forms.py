# trong tệp forms.py
from django import forms
from .models import ProductRating, Product

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductRating
        fields = ['rating']

class ProductDescriptionForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['customer_description']
