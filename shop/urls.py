from django.urls import path

from shop.views import ProductDetailView, test_view

urlpatterns = [
    path("", test_view, name="base"),
    path("products/<str:ct_model>/<str:slug>/", ProductDetailView.as_view(), name="product_detail"),
]
