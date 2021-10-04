from django.urls import path

from shop.views import ProductDetailView, test_view, CategoryDetailView

urlpatterns = [
    path("", test_view, name="base"),
    path("products/<str:ct_model>/<str:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path("category/<str:slug>/", CategoryDetailView.as_view(), name="category_detail"),
]
