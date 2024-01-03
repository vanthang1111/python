from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator, MaxValueValidator



# Create your models here.#change forms register django

class Category(models.Model):
    sub_cayegory = models.ForeignKey('self',on_delete=models.CASCADE,related_name='sub_categories',null=True,blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200,null=True)
    slug =models.SlugField(max_length=200,null=True)
    def __str__(self):
        return self.name

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields=['username','email','first_name','last_name','password1','password2']
        

    
class Product(models.Model):
    category=models.ManyToManyField(Category,related_name='product')
    name = models.CharField(max_length=200,null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False,null=True,blank=False)
    image=models.ImageField(null=True,blank=True)
    detail = models.TextField(null=True,blank=True)
    is_discounted = models.BooleanField(default=False)
    discount_percent = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    customer_description = models.TextField(blank=True, null=True)
    purchase_count = models.IntegerField(default=0)
    def get_discounted_price(self):
        discount_amount = (self.discount_percent / 100) * self.price
        discounted_price = self.price - discount_amount
        return discounted_price
    def __str__(self):
        return self.name
    @property
    def ImageURL(self):
        try:
            url=self.image.url
        except:
            url=''
        return url

class Order(models.Model):
    customer = models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
    date_order= models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    complete = models.BooleanField(default=False,null=True,blank=False)
    transiction_id=models.CharField(max_length=200,null=True)
    
    def __str__(self):
        # return str(self.id)
        return f"{self.customer.username} - {self.id}"
    @property
    def get_cart_items(self):
     orderitems=self.orderitem_set.all()
     total =sum([item.quantity for item in orderitems])
     return total
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.discounted_total for item in orderitems])
        return total
    @property
    def discounted_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total_discounted for item in orderitems])
        return total
class Orderitem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,blank=True,null=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    quantity = models.IntegerField(default=0,null=True,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    # Thêm trường discounted_price để lưu giá giảm giá
    discounted_price = models.FloatField(default=0)
    @property
    def discounted_total(self):
        return self.product.get_discounted_price() * self.quantity if self.product.is_discounted else self.product.price * self.quantity
    @property
    def get_total(self):
        total = self.discounted_price * self.quantity  # Sử dụng giá giảm giá
        return total
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    @property
    def get_total_discounted(self):
        if self.product.is_discounted:
            return self.quantity * self.product.get_discounted_price()
        else:
            return self.quantity * self.product.price

# models.py
class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)  # Giả sử có thang đánh giá từ 1-5

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating} stars"

  
class ShippingAddress(models.Model):
    customer = models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    address = models.CharField(max_length=200,null=True)
    city = models.CharField(max_length=200,null=True)
    state = models.CharField(max_length=200,null=True)
    mobile = models.CharField(max_length=200,null=True)
    country = models.CharField(max_length=200,null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.id)
class PaymentInfo(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255)
    payer_id = models.CharField(max_length=255)
    # Thêm các trường khác tùy ý

    def __str__(self):
        return f"{self.order} - {self.payment_id}"