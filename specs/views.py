from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, ListView

from shop.models import Category
from specs.forms import NewCategoryForm, NewCategoryFeatureKeyForm
from specs.models import CategoryFeature


class BaseSpecView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "specs/product_features.html")


class CreateNewCategoryView(CreateView):
    form_class = NewCategoryForm
    template_name = "specs/new_category.html"
    success_url = "/product-specs/"


class CreateNewFeatureView(CreateView):
    form_class = NewCategoryFeatureKeyForm
    template_name = "specs/new_feature.html"
    success_url = "/product-specs/"


# class CreateNewFeatureValidator(ListView):
#     template_name = "specs/new_validator.html"
#     model = Category
#     context_object_name = "categories"


class CreateNewFeatureValidator(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        context = {"categories": categories}
        return render(request, "specs/new_validator.html", context)


class FeatureChoiceView(View):
    def get(self, request, *args, **kwargs):
        option = '<option value="{value}">{option_name}</option>'
        html_select = """
            <select class="form-select" name="feature-validators" id="feature-validators-id" aria-label="Default select example">
                <option selected>---</option>
                {result}
            </select>
                    """
        feature_key_qs = CategoryFeature.objects.filter(category_id=int(request.GET.get("category_id")))
        res_string = ""
        for item in feature_key_qs:
            res_string += option.format(value=item.feature_name, option_name=item.feature_name)
        html_select = html_select.format(result=res_string)
        return JsonResponse({"result": html_select, "value": int(request.GET.get("category_id"))})
