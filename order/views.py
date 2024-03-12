from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseServerError

from basket.basket import Basket
from store.models import Product
from .forms import OrderForm
from .models import Order
from basket.utils import create_order_from_basket
from django.contrib.auth.decorators import login_required


@login_required
def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                basket = Basket(request)
                for item in basket:
                    product = item['product']
                    quantity = item['qty']
                user = request.user
                order = create_order_from_basket(user, basket)
                for item in basket:
                    product = item['product']
                    quantity = item['qty']
                    product.stock -= quantity
                    product.save()
                request.session['skey'] = {}
                return redirect('order:order_confirmation', order_id=order.id)
            except Exception as e:
                print("Error:", e)
                return HttpResponseServerError("An error occurred while placing the order.")
    else:
        pass


def order_confirmation(request, order_id):
    user = request.user
    order = Order.objects.get(id=order_id)
    products = Product.objects.filter(created_by=user)
    return render(request, 'order_confirmation.html', {'order': order,'products':products})


@login_required(login_url='/accounts/signin/')
def order_list(request):
    if request.user.groups.filter(name='StoreAdmin').exists():
        orders = Order.objects.all().order_by('-created_at')
        return render(request, 'order/order_list.html', {'orders': orders})
    else:
        return render(request, 'accounts/signin.html')


def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order/order_detail.html', {'order': order})


@login_required(login_url='/accounts/signin/')
def update_order_status(request, order_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()
        return redirect('order:order_list')
    else:
        pass


def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    for order in orders:
        for item in order.orderitem_set.all():
            if item.product.discounted_price:
                item_price = item.product.discounted_price
            else:
                item_price = item.product.price
            item.item_price = item_price
    return render(request, 'order/my_orders.html', {'orders': orders})