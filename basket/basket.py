from decimal import Decimal
from store.models import Product

class Basket():

    def __init__(self, request):
        self.session = request.session
        basket = self.session.get('skey')
        if 'skey' not in request.session:
            basket = self.session['skey'] = {}
        self.basket = basket

    def add(self, product, qty, discounted_price=None):
        product_id = str(product.id)
        if product_id in self.basket:
            self.basket[product_id]['qty'] += qty
        else:
            if discounted_price:
                price = str(discounted_price)
            else:
                price = str(product.price)
            self.basket[product_id] = {'price': price, 'qty': qty}
        self.save()

    def __iter__(self):
        product_ids = self.basket.keys()
        products = Product.products.filter(id__in=product_ids)
        basket = self.basket.copy()

        for product in products:
            basket[str(product.id)]['product'] = product

        for item in basket.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['qty']
            yield item

    def __len__(self):
        return sum(item['qty'] for item in self.basket.values())

    def update(self, product_id, qty):
        product_id = str(product_id)
        if product_id in self.basket:
            self.basket[product_id]['qty'] = qty
            try:
                product = Product.objects.get(id=product_id)
                if product.discounted_price is not None:
                    self.basket[product_id]['price'] = str(product.discounted_price)
                else:
                    self.basket[product_id]['price'] = str(product.price)
            except Product.DoesNotExist:
                pass
        self.save()
    def get_subtotal_price(self):
        subtotal_price = sum(
            Decimal(item.get('product').discounted_price if item.get('product') and item.get(
                'product').discounted_price else item.get('product').price) *
            item['qty']
            for item in self.basket.values() if 'product' in item
        )
        return subtotal_price

    def get_total_price(self):
        total_price = sum(
            (Decimal(item['product'].discounted_price) * item['qty'])
            if item.get('product') and item['product'].discounted_price is not None
            else (Decimal(item['price']) * item['qty'] + 30)
            for item in self.basket.values()
        )
        return total_price

    def delete(self, product_id):
        product_id = str(product_id)
        if product_id in self.basket:
            del self.basket[product_id]
            self.save()

    def save(self):
        self.session.modified = True
