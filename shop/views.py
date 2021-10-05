from django.shortcuts import render
from django.views.generic import DetailView, View

from shop.models import Notebook, Smartphone, Category, LatestProducts
from shop.mixins import CategoryDetailMixin


class BaseView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        products = LatestProducts.objects.get_products_for_main_page(
            "notebook", "smartphone", with_respect_to="smartphone"
        )
        context = {"categories": categories, "products": products}
        return render(request, "shop/base.html", context)


def test_view(request):
    categories = Category.objects.get_categories_for_left_sidebar()
    return render(request, "shop/base.html", {"categories": categories})


class ProductDetailView(CategoryDetailMixin, DetailView):
    CT_MODEL_MODEL_CLASS = {"notebook": Notebook, "smartphone": Smartphone}

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs["ct_model"]]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    context_object_name = "product"
    template_name = "shop/product_detail.html"
    slug_url_kwarg = "slug"


class CategoryDetailView(CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = "categories"
    template_name = "shop/category_detail.html"
    slug_url_kwarg = "slug"
