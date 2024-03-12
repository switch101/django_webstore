from django.contrib.auth.decorators import login_required
from django.core.checks import messages

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from store.models import Product
from .basket import Basket


# Create your views here.


def basket_summary(request):
    basket = Basket(request)
    subtotal_price = basket.get_subtotal_price()
    context = {
        'basket': basket,
        'subtotal_price': subtotal_price,
    }
    return render(request, 'store/basket/summary.html', context)


def basket_add(request):
    basket = Basket(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        product_qty = int(request.POST.get('productqty'))
        product = get_object_or_404(Product, id=product_id)
        basket.add(product=product, qty=product_qty)
        basketqty = basket.__len__()
        response = JsonResponse({'qty': basketqty})
        messages.success(request, f"{product.title} has been added to your cart.")
        return response


def basket_delete(request):
    basket = Basket(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        basket.delete(product_id=product_id)
        basketqty = basket.__len__()
        baskettotal = basket.get_total_price()
        response = JsonResponse({'qty': basketqty, 'subtotal': baskettotal})
        return response


def basket_update(request):
    basket = Basket(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        product_qty = int(request.POST.get('productqty'))
        basket.update(product_id, qty=product_qty)
        basketqty = len(basket)
        baskettotal = basket.get_total_price()
        response = JsonResponse({'qty': basketqty, 'subtotal': baskettotal})
        return response


@login_required(login_url='signin')
def checkout(request):
    if request.method == 'POST':
        basket = Basket(request)
        user = request.user
        checkout = basket.create_checkout(user)
        total_price = checkout.get_total_price()
        checkout.create_order()
        basket.clear()
        messages.success(request, 'Order placed successfully!')
        return redirect('')
    else:
        pass

    return render(request, 'store/basket/checkout.html')
