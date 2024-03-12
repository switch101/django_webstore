from order.forms import OrderForm
from order.models import OrderItem

from order.models import Order


def create_order_from_basket(user, basket):
    order = Order(user=user, total_price=basket.get_total_price())
    order.save()
    for item in basket:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['qty'],
            price=item['price']
        )
    return order
