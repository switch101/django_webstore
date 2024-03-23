import sib_api_v3_sdk
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseServerError
from django.core.mail import send_mail
from django.conf import settings
# from sib_api_v3_sdk import TransactionalEmailsApi, SendSmtpEmail
# from sib_api_v3_sdk.models import SendSmtpEmailSender, SendSmtpEmailTo
# from sib_api_v3_sdk.rest import ApiException

from basket.basket import Basket
from store.models import Product
from .forms import OrderForm
from .models import Order
from basket.utils import create_order_from_basket
from django.contrib.auth.decorators import login_required


# def send_email_with_sendinblue(email, subject, content):
#     try:
#         configuration = sib_api_v3_sdk.Configuration()
#         configuration.api_key['api-key'] = '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'
#         api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
#
#         send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
#             sender={'email': 'gabiswitch97@icloud.com'},
#             to=[{'email': email}],
#             subject=subject,
#             html_content=content
#         )
#
#         api_response = api_instance.send_transac_email(send_smtp_email)
#         return True
#     except ApiException:
#         return False

@login_required
def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                basket = Basket(request)
                user = request.user
                order = create_order_from_basket(user, basket)

                # subject = 'Order Placed Successfully'
                # message = f'Your order with ID {order.id} has been successfully placed.'
                # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                #
                # email_subject = 'Order Placed Successfully'
                # email_content = f'Your order with ID {order.id} has been successfully placed.'
                # send_email_with_sendinblue(user.email, email_subject, email_content)

                for item in basket:
                    product = item['product']
                    quantity = item['qty']
                    product.stock -= quantity
                    product.save()

                request.session['skey'] = {}

                return redirect('order:order_confirmation', order_id=order.id)
            except Exception as e:
                print(f"An error occurred while placing the order: {e}")
                return HttpResponseServerError("An error occurred while placing the order.")


@login_required
def order_confirmation(request, order_id):
    user = request.user
    order = Order.objects.get(id=order_id)
    products = Product.objects.filter(created_by=user)
    return render(request, 'order_confirmation.html', {'order': order, 'products': products})


@login_required
def order_list(request):
    if request.user.groups.filter(name='StoreAdmin').exists():
        orders = Order.objects.all().order_by('-created_at')
        return render(request, 'order/order_list.html', {'orders': orders})
    else:
        return render(request, 'accounts/signin.html')


@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()
        #
        # email_subject = 'Order Status Update'
        # email_content = f'Your order with ID {order.id} has been updated to {new_status}.'
        # send_email_with_sendinblue(order.user.email, email_subject, email_content)

        return redirect('order:order_list')
    else:
        pass


@login_required
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


def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order/order_detail.html', {'order': order})
