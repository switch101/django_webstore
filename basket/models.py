from decimal import Decimal

from store.models import Product


class Checkout:
    def __init__(self, user):
        self.user = user
        self.items = []

    def add_item(self, product, qty, price, discounted_price=None):
        if discounted_price is not None:
            total_price = Decimal(discounted_price) * qty
        else:
            total_price = Decimal(price) * qty

        item = {
            'product': product,
            'qty': qty,
            'price': price,
            'discounted_price': discounted_price,
            'total_price': total_price
        }
        self.items.append(item)

    def get_total_price(self):
        return sum(item['total_price'] for item in self.items)


class Basket:
    def __init__(self, request):
        self.session = request.session
        basket = self.session.get('skey', {})
        if 'skey' not in request.session:
            self.session['skey'] = basket
        self.basket = basket

    def add(self, product, qty):
        product_id = str(product.id)
        if product.discounted_price is not None:
            price = str(product.discounted_price)
        else:
            price = str(product.price)

        if product_id in self.basket:
            self.basket[product_id]['qty'] += qty
        else:
            self.basket[product_id] = {'price': price, 'qty': qty}

        self.save()

    def __iter__(self):
        product_ids = self.basket.keys()
        products = Product.objects.filter(id__in=product_ids)

        basket = self.basket.copy()
        for product in products:
            basket[str(product.id)]['product'] = product

        for item in basket.values():
            product = Product.objects.get(id=item['product'].id)
            if product.discounted_price is not None:
                item['price'] = Decimal(item['product'].discounted_price)
                item['total_price'] = Decimal(item['product'].discounted_price) * item['qty']
            else:
                item['price'] = Decimal(item['product'].price)
                item['total_price'] = Decimal(item['product'].price) * item['qty']
            yield item

    def __len__(self):
        return sum(item['qty'] for item in self.basket.values())

    def update(self, product, qty):
        product_id = str(product.id)

        if product_id in self.basket:
            self.basket[product_id]['qty'] = qty
            self.save()

    def delete(self, product):
        product_id = str(product.id)
        if product_id in self.basket:
            del self.basket[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def create_checkout(self, user):
        checkout = Checkout(user)
        for product_id, item in self.basket.items():
            product = Product.objects.get(id=product_id)
            price = product.discounted_price if product.discounted_price is not None else product.price
            checkout.add_item(product, item['qty'], price)
        return checkout