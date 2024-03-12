from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.product_all, name='product_all'),
    path('<slug:slug>', views.product_detail, name='product_detail'),
    path('shop/<slug:category_slug>/', views.category_list, name='category_list'),
    path('add_book/', views.add_book, name='add_book'),
    path('search/', views.product_search, name='product_search'),
    path('submit_review/', views.submit_review, name='submit_review'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_to_favorites/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/', views.favorite_products, name='favorite_products'),
    path('remove-from-favorites/<int:product_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('category/add/', views.add_category, name='add_category'),
    path('edit-product/<slug:slug>/', views.edit_product, name='edit_product'),
    path('all-books/', views.view_all_books, name='view_all_books'),

]
