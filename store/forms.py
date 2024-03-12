from django import forms
from .models import Product, Review, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'title', 'author', 'description', 'image', 'price', 'discounted_price', 'in_stock',
                  'is_active', 'sku', 'stock']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['discounted_price'].required = False


class ProductSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)


class ReviewForm(forms.ModelForm):
    product_id = forms.IntegerField()

    class Meta:
        model = Review
        fields = ['review', 'star_rating']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
