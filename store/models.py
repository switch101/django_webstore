from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.utils.text import slugify
from django_webstore import settings


class Review(models.Model):
    product = models.ForeignKey('Product', related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.TextField(blank=True)
    star_rating = models.IntegerField(default=0)


class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(is_active=True)


class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('store:category_list', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products_created')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, default='')
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=30)
    stock = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    image = models.ImageField(upload_to='images/', default='images/default.jpg')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favorite_products')
    objects = models.Manager()
    products = ProductManager()

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        self.calculate_rating()

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    def __str__(self):
        return self.title

    def calculate_rating(self):
        avg_rating = self.reviews.aggregate(Avg('star_rating'))['star_rating__avg']
        self.rating = avg_rating if avg_rating is not None else 0

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.calculate_rating()

    def calculate_discount_percentage(self):
        if self.discounted_price is not None:
            return round((1 - (self.discounted_price / self.price)) * 100, 0)
        return None
