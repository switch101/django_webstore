from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.http import JsonResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404

from order.models import Order
from .models import Category
from .forms import ProductForm, ProductSearchForm, CategoryForm
from django.shortcuts import render, redirect
from .models import Product, Review
from .forms import ReviewForm


# Create your views here.

def product_all(request):
    products = Product.products.filter(is_active=True).annotate(avg_rating=Avg('reviews__star_rating'))
    return render(request, 'store/home.html', {'products': products})


def category_list(request, category_slug=None):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_active=True).annotate(
        avg_rating=Avg('reviews__star_rating'))
    return render(request, 'store/products/category.html', {'category': category, 'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if product.is_active and product.in_stock:
        reviews = product.reviews.all()
        recommended_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:5]
        user_has_reviewed = False
        avg_rating = reviews.aggregate(Avg('star_rating'))['star_rating__avg']

        if request.user.is_authenticated:
            user_has_reviewed = product.reviews.filter(user=request.user).exists()

            if request.method == 'POST':
                form = ReviewForm(request.POST)
                if form.is_valid():
                    review = form.cleaned_data['review']
                    star_rating = form.cleaned_data['star_rating']
                    user = request.user
                    Review.objects.create(product=product, user=user, review=review, star_rating=star_rating)
                    return redirect(product)
            else:
                form = ReviewForm()
        else:
            form = None
        return render(request, 'store/products/single.html',
                      {'product': product, 'form': form, 'avg_rating': avg_rating,
                       'recommended_products': recommended_products, 'user_has_reviewed': user_has_reviewed})
    else:
        return render(request, 'store/home.html')


def add_book(request):
    if request.user.groups.filter(name='StoreAdmin').exists():
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)
                product.created_by = request.user
                product.save()
                return redirect('store:dashboard')
            else:
                print(form.errors)
        else:
            form = ProductForm()
        return render(request, 'store/add_book.html', {'form': form})
    else:
        return render(request, 'accounts/signin.html')


def product_search(request):
    form = ProductSearchForm()
    query = request.GET.get('query')
    products = []

    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query),
            is_active=True
        )

    context = {
        'form': form,
        'query': query,
        'products': products
    }

    return render(request, 'store/product_search.html', context)


def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            review_text = form.cleaned_data['review']
            rating = form.cleaned_data['star_rating']
            product = get_object_or_404(Product, id=product_id)
            review = Review.objects.create(product=product, user=request.user, review=review_text, star_rating=rating)
            product.rating = product.reviews.aggregate(Avg('star_rating'))['star_rating__avg']
            product.save()
            data = {
                'username': review.user.username,
                'rating': review.star_rating,
                'review': review.review
            }
            return JsonResponse(data)
    else:
        form = ReviewForm()
    return redirect('store:all_products')


@login_required(login_url='/accounts/signin/')
def dashboard(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    orders = Order.objects.all()
    return render(request, 'store/dashboard.html', {'categories': categories, 'orders': orders, 'products': products})


@login_required(login_url='/accounts/signin/')
def add_to_favorites(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        request.user.favorite_products.add(product)
        return JsonResponse({'message': 'Product added to favorites successfully'}, status=200)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)


@login_required(login_url='/accounts/signin/')
def favorite_products(request):
    user = request.user
    if user.is_authenticated:
        favorite_products = Product.objects.filter(favorites=user)
        return render(request, 'store/favorite_products.html', {'favorite_products': favorite_products})
    else:
        return render(request, 'store/favorite_products.html', {})


@login_required(login_url='/accounts/login/')
def remove_from_favorites(request, product_id):
    if request.method == 'POST' and request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        request.user.favorite_products.remove(product)
        return JsonResponse({'message': 'Product removed from favorites successfully'}, status=200)
    else:
        return JsonResponse({'error': 'User not authenticated or request method is not POST'}, status=401)


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store:dashboard')
    else:
        form = CategoryForm()
    return render(request, 'store/products/add_category.html', {'form': form})


def edit_product(request, slug):
    product = Product.objects.get(slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            if 'discounted_price' not in form.cleaned_data:
                product.discounted_price = None
            form.save()
            return redirect('store:dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/products/edit_book.html', {'form': form, 'product': product})


def view_all_books(request):
    all_books = Product.objects.all()  # Assuming Product is your model for books
    return render(request, 'store/products/all_books.html', {'all_books': all_books})
