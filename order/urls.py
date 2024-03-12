from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.order_list, name='order_list'),
    path('order_detail/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('update_status/<int:order_id>/', views.update_order_status, name='update_status'),
    path('my_orders/', views.my_orders, name='my_orders'),

]
