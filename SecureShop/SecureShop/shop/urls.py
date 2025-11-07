from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("admin/products/new/", views.product_new, name="product_new"),
    path("admin/products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("login/verify/", views.login_verify, name="login_verify"),
    path("orders/", views.orders_mine, name="orders_mine"),


]
