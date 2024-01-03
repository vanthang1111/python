from django.contrib import admin
from django.urls import path,include
from .views import process_order
from . import views
from .views import  gioithieu
from paypal.standard.ipn import urls as paypal_urls
from django.views.decorators.csrf import csrf_exempt
from .views import detail
from .views import best_selling_products
urlpatterns = [
     path('detail/<int:product_id>/', detail, name='product_detail'),
     path('', views.home,name="home"),
     # Mẫu URL khác nhau
     path('paypal/', views.paypal_return, name='paypal_return'),
     path('paypal/ipn/', include(paypal_urls)),

     path('paypal_return/', views.paypal_return, name='paypal_return'),
     path('register/',views.register,name="register"),
     path('thank_you/', views.thank_you, name='thank_you'),
     path('paypal/', include(paypal_urls)),
     path('login/',views.loginPage,name="login"),
     path('search/',views.search,name="search"),
     path('category/',views.category,name="category"),
     path('detail/',views.detail,name="detail"),
     path('process_order/', process_order, name='process_order'),
     path('logout/',views.logoutPage,name="logout"),
     path('cart/',views.cart,name="cart"),
     path('checkout/',views.checkout,name="checkout"),
     path('update_item/',views.updateItem,name="update_item"),
     path('best-selling/', best_selling_products, name='best_selling_products'),
]
