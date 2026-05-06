from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.customer_signup, name='customer_signup'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_home/', views.admin_home, name='admin_home'),

    # STAFF
    path('manage_staff/', views.manage_staff, name='manage_staff'),
    path('add_staff/', views.add_staff, name='add_staff'),
    path('edit_staff/<int:user_id>/', views.edit_staff, name='edit_staff'),
    path('delete_staff/<int:user_id>/', views.delete_staff, name='delete_staff'),

    # CUSTOMER
    path('manage_customers/', views.manage_customers, name='manage_customers'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('delete_customer/<int:user_id>/', views.delete_customer, name='delete_customer'),

    # INVENTORY (STAFF DASHBOARD)
    path('staff_home/', views.staff_home, name='staff_home'),
    path('add_item/', views.add_item, name='add_item'),
    path('edit_item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete_item/<int:item_id>/', views.delete_item, name='delete_item'),

    # CUSTOMER DASHBOARD
    path('customer_home/', views.customer_home, name='customer_home'),
    path('cart/', views.cart_view, name='cart'),
]