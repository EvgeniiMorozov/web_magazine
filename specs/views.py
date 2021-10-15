from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView

from specs.forms import NewCategoryForm


class BaseSpecView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "specs/product_features.html")


class NewCategoryView(CreateView):
    form_class = NewCategoryForm
    template_name = "specs/new_category.html"
    success_url = ("/product-specs/")
