from django.shortcuts import render,redirect
from django.http import HttpResponse ,JsonResponse
from .models import ShippingAddress as SA
from paypalrestsdk import Payment
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from paypalrestsdk import Payment
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.http import HttpResponseRedirect

# Trong views.py
from .forms import ProductReviewForm, ProductDescriptionForm

import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
# Create your views here.
@csrf_exempt
def process_paypal_payment(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ PayPal
        payment_id = request.POST.get('paymentID')
        payer_id = request.POST.get('payerID')

        # Xác nhận thanh toán với PayPal
        payment = Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            # Lưu thông tin thanh toán vào cơ sở dữ liệu Django
            order = Order.objects.filter(complete=False).first()
            order.payment_id = payment_id
            order.save()

            # Xóa đơn hàng trong giỏ hàng
            order_items = order.orderitem_set.all()
            order_items.delete()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Payment execution failed'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

def detail(request,product_id):
    if request.user.is_authenticated:
        customer=request.user
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login="hidden"
        user_login="show"
    else:
        items=[]
        order={'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
        user_not_login="show"
        user_login="hidden"
    categories = Category.objects.filter(is_sub=False)
    id = request.GET.get('id', '')
    products = Product.objects.get(id=product_id)
    ratings = ProductRating.objects.filter(product_id=product_id)
    description_form = ProductDescriptionForm(instance=products)
    review_form = ProductReviewForm()

    if request.method == 'POST':
        if 'rating' in request.POST:
            # Kiểm tra xem người dùng đã đánh giá sản phẩm này chưa
            existing_rating = ProductRating.objects.filter(product=products, user=request.user)
            if existing_rating.exists():
                # Nếu đã đánh giá, bạn có thể xử lý theo cách nào đó, ví dụ: thông báo lỗi hoặc chuyển hướng đến trang khác
                return HttpResponseRedirect(reverse('home'))  # Chuyển hướng về trang chủ, bạn có thể thay đổi URL tùy ý

            review_form = ProductReviewForm(request.POST)
            if review_form.is_valid():
                rating = review_form.save(commit=False)
                rating.user = request.user
                rating.product = products
                rating.save()
                messages.success(request, 'Đã đánh giá sản phẩm thành công.')

        elif 'customer_description' in request.POST:
            description_form = ProductDescriptionForm(request.POST, instance=products)
            if description_form.is_valid():
                description_form.save()

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'categories': categories,
        'product': products,  # Đổi tên biến để tránh nhầm lẫn với tên model 'Product'
        'ratings': ratings,
        'description_form': description_form,
        'review_form': review_form,
        'user_has_rated': ProductRating.objects.filter(product=products, user=request.user).exists(),
    }

    return render(request, 'app/detail.html', context)

def register(request):
    form = CreateUserForm()
    user_not_login = "hidden"
    user_login = "hidden"  
    if request.method =="POST":
        form=CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('login')

    context={'form':form,'user_not_login': user_not_login, 'user_login': user_login}
    return render(request,'app/register.html',context)
def loginPage(request):
    user_not_login = "hidden"
    user_login = "hidden"  # Giả sử mặc định là ẩn, bạn có thể thay đổi nếu cần

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
            user_not_login = "hidden"
            user_login = "show"
        else:
            user_not_login = "show"
            user_login = "hidden"
            messages.info(request, 'Tài khoản hoặc mật khẩu sai')

    context = {'user_not_login': user_not_login, 'user_login': user_login}
    return render(request, 'app/login.html', context)


def logoutPage(request):
    logout(request)
    return redirect('login')

def category(request):
    if request.user.is_authenticated:
     categories = Category.objects.filter(is_sub=False)
     active_category = request.GET.get('category', '')
     products = None  # Khởi tạo products là None
     customer=request.user
     if active_category:
        products = Product.objects.filter(category__slug=active_category)
     user_not_login="hidden"
     user_login="show"
     order,created=Order.objects.get_or_create(customer=customer,complete=False)
     items=order.orderitem_set.all()
     cartItems = order.get_cart_items
    else:
     user_not_login="show"
     user_login="hidden"
     items=[]
     order={'get_cart_items':0,'get_cart_total':0 }
     cartItems = order['get_cart_items']
    context = {'categories': categories,'cartItems':cartItems, 'products': products, 'active_category': active_category,'user_login':user_login,'user_not_login':user_not_login}
    return render(request, 'app/category.html', context)


def search(request):
    if request.method =="POST":
        searched = request.POST["searched"]
        keys=Product.objects.filter(name__icontains = searched)
    if request.user.is_authenticated:
        customer=request.user
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login="hidden"
        user_login="show"
    else:
        items=[]
        order={'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
        user_not_login="show"
        user_login="hidden"
    products=Product.objects.all()
    categories = Category.objects.filter(is_sub=False)

    
    return render(request,'app/search.html',{"searched" : searched,"keys" : keys,'products':products,'cartItems':cartItems,'user_not_login':user_not_login,'user_login':user_login,'categories':categories})
def home(request):
    
    if request.user.is_authenticated:
        customer=request.user
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login="hidden"
        user_login="show"
    else:
        items=[]
        order={'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
        user_not_login="show"
        user_login="hidden"
    all_products = Product.objects.filter(is_discounted=False)
    categories = Category.objects.filter(is_sub=False)
         # Lọc sản phẩm giảm giá và tất cả sản phẩm
    discount_products = Product.objects.filter(is_discounted=True)
    all_products = Product.objects.filter(is_discounted=False)

    # Phân trang cho sản phẩm giảm giá
    page_discount = request.GET.get('page_discount', 1)
    paginator_discount = Paginator(discount_products, 4)  # Hiển thị 4 sản phẩm trên mỗi trang
    try:
        discount_products = paginator_discount.page(page_discount)
    except PageNotAnInteger:
        discount_products = paginator_discount.page(1)
    except EmptyPage:
        discount_products = paginator_discount.page(paginator_discount.num_pages)

        # Phân trang cho tất cả sản phẩm
    page_all = request.GET.get('page_all', 1)
    paginator_all = Paginator(all_products, 4)
    try:
        paginated_all_products = paginator_all.page(page_all)
    except PageNotAnInteger:
        paginated_all_products = paginator_all.page(1)
    except EmptyPage:
        paginated_all_products = paginator_all.page(paginator_all.num_pages)

    context = {
        'discount_products': discount_products,
        'all_products': paginated_all_products,  # Đổi tên biến
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'categories': categories
    }

    return render(request, 'app/home.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"

    # Thêm giá giảm giá vào mỗi item trong giỏ hàng
    for item in items:
        if item.product.is_discounted:
            item.discounted_price = item.product.get_discounted_price()

    # Lấy giá giảm giá từ sản phẩm
    discounted_price = 0
    for item in items:
        discounted_price += item.discounted_price
    discounted_total = order.discounted_total
    categories = Category.objects.filter(is_sub=False)
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'categories': categories,
        'discounted_price': discounted_price,
        'discounted_total': discounted_total,  # Thêm discounted_total vào context
    }

    return render(request, 'app/cart.html', context)


from django.shortcuts import render, redirect
def gioithieu(request):
    return render(request, 'gioithieu.html')

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"

    categories = Category.objects.filter(is_sub=False)

    if request.method == 'POST':
        # Xử lý việc gửi biểu mẫu
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        mobile = request.POST.get('mobile')
        country = request.POST.get('country')

        # Kiểm tra tính hợp lệ của dữ liệu (bạn có thể thêm kiểm tra hợp lệ khác)
        if name and email and address and city and state and mobile and country:
            # Lưu thông tin vận chuyển vào mô hình ShippingAddress
            shipping_address = ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=address,
                state=state,
                mobile=mobile,
                city=city,
                country=country
            )

            # Kiểm tra xem order có tồn tại không trước khi truy cập thuộc tính complete
            if order and hasattr(order, 'complete'):
                order.complete = True
                order.save()
                # Chuyển hướng người dùng đến trang cảm ơn hoặc trang xác nhận đơn hàng
                #return render(request, 'app/thank_you.html', {'order': order, 'shipping_address': shipping_address})
                return redirect('thank_you/')
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'categories': categories,
        'discounted_total': order.get_cart_total,  # Thêm giá giảm giá vào context
    }
    return render(request, 'app/checkout.html', context)



def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = Orderitem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse({'added': True})

from paypalrestsdk import Payment
from .models import Orderitem, ShippingAddress, PaymentInfo
from django.http import JsonResponse
from django.shortcuts import render

def process_order(request):
    if request.method == 'POST':
        try:
            # Xử lý dữ liệu từ biểu mẫu thanh toán
            name = request.POST.get('name')
            email = request.POST.get('email')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            mobile = request.POST.get('mobile')
            country = request.POST.get('country')

            # Xử lý thông tin đơn hàng
            if name and email and address and city and state and mobile and country:
                # Lưu thông tin vận chuyển vào mô hình ShippingAddress
                order = request.user.order_set.filter(complete=False).first()
                shipping_address = ShippingAddress.objects.create(
                    customer=request.user,
                    order=order,
                    address=address,
                    city=city,
                    state=state,
                    mobile=mobile,
                    country=country
                )

                # Cập nhật trạng thái đơn hàng
                order.is_paid = True
                order.complete = True
                order.save()
# Trong hàm process_order
                for item in order.orderitem_set.all():
                    item.product.purchase_count += item.quantity
                    item.product.save()

                # Tạo thanh toán PayPal
                payment = Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal",
                    },
                    "redirect_urls": {
                        "return_url": request.build_absolute_uri(reverse('paypal_return')),
                        "cancel_url": request.build_absolute_uri('/paypal/cancel/'),
                    },
                    "transactions": [
                        {
                            "item_list": {
                                "items": [
                                    {
                                        "name": f"Order #{order.id}",
                                        "sku": "item",
                                        "price": str(order.get_cart_total),
                                        "currency": "USD",
                                        "quantity": 1,
                                    },
                                ],
                            },
                            "amount": {
                                "total": str(order.get_cart_total),
                                "currency": "USD",
                            },
                            "description": f"Payment for Order #{order.id}",
                        }
                    ],
                })

                if payment.create():
                    print("Payment created successfully")

                   
                    
                    # Lưu payment_id vào session
                    request.session['payment_id'] = payment.id

                    # Xóa sản phẩm từ giỏ hàng
                    order.orderitem_set.all().delete()

                    # Tạo và lưu thông tin thanh toán vào PaymentInfo
                    payment_info = PaymentInfo.objects.create(
                        order=order,
                        payment_id=payment.id,
                        payer_id=request.GET.get('PayerID')  # Thêm các trường khác tùy ý
                    )

                    return JsonResponse({'redirect_url': payment.links[1].href})

                else:
                    print(f"Error creating payment: {payment.error}")

        except Exception as e:
            print(f"Error processing order: {e}")

    # Nếu đơn hàng đã hoàn thành, chuyển hướng đến trang cảm ơn
    # if order.complete:
    #     return redirect('thank_you.hmtl')

    # status = 0
    # print(status)
    return render(request, 'app/checkout.html')

# Trong hàm paypal_return
def paypal_return(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    # Lấy payment_id từ session hoặc database (tùy thuộc vào cách bạn lưu trữ)
    payment_id_session = request.session.get('payment_id')

    if payment_id_session:
        payment = Payment.find(payment_id_session)

        try:
            if payment.execute({"payer_id": payer_id}):
                print("Payment executed successfully")

                # Lưu thông tin thanh toán vào đơn hàng Django
                order = Order.objects.filter(complete=False, payment_id=payment_id_session).first()
                if order:
                    order.payment_id = payment_id_session
                    order.is_paid = True
                    order.save()

                    # Lưu thông tin thanh toán vào PaymentInfo
                    payment_info = PaymentInfo.objects.create(
                        order=order,
                        payment_id=payment_id_session,
                        payer_id=payer_id  # Thêm các trường khác tùy ý
                    )

                    # Xóa sản phẩm từ giỏ hàng
                    Orderitem.objects.filter(order=order).delete()

                    # Xóa payment_id từ session sau khi xử lý thành công
                    del request.session['payment_id']

                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Invalid order associated with payment_id'})

            else:
                return JsonResponse({'success': False, 'error': 'Payment execution failed'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error processing payment: {e}'})

    return JsonResponse({'success': False, 'error': 'Invalid payment_id'})


from django.shortcuts import render

def thank_you(request):
    # Xử lý và trả về template cảm ơn
    return render(request, 'app/thank_you.html')

def best_selling_products(request):
    if request.user.is_authenticated:
        customer=request.user
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login="hidden"
        user_login="show"
    else:
        items=[]
        order={'get_cart_items':0,'get_cart_total':0 }
        cartItems = order['get_cart_items']
        user_not_login="show"
        user_login="hidden"
    all_products = Product.objects.filter(is_discounted=False)
    categories = Category.objects.filter(is_sub=False)
         # Lọc sản phẩm giảm giá và tất cả sản phẩm
    discount_products = Product.objects.filter(is_discounted=True)
    all_products = Product.objects.filter(is_discounted=False)

    # Phân trang cho sản phẩm giảm giá
    page_discount = request.GET.get('page_discount', 1)
    paginator_discount = Paginator(discount_products, 9)  # Hiển thị 4 sản phẩm trên mỗi trang
    try:
        discount_products = paginator_discount.page(page_discount)
    except PageNotAnInteger:
        discount_products = paginator_discount.page(1)
    except EmptyPage:
        discount_products = paginator_discount.page(paginator_discount.num_pages)

        # Phân trang cho tất cả sản phẩm
    page_all = request.GET.get('page_all', 1)
    paginator_all = Paginator(all_products, 4)
    try:
        paginated_all_products = paginator_all.page(page_all)
    except PageNotAnInteger:
        paginated_all_products = paginator_all.page(1)
    except EmptyPage:
        paginated_all_products = paginator_all.page(paginator_all.num_pages)

    context = {
        'discount_products': discount_products,
        'all_products': paginated_all_products,  # Đổi tên biến
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'categories': categories
    }

    return render(request, 'app/best_selling_products.html', context)

