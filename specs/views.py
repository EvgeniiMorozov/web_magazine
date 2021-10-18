from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, ListView

from shop.models import Category, Product
from specs.forms import NewCategoryForm, NewCategoryFeatureKeyForm
from specs.models import CategoryFeature, FeatureValidator


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
        res_string = "".join(
            option.format(value=item.feature_name, option_name=item.feature_name) for item in feature_key_qs
        )

        html_select = html_select.format(result=res_string)
        return JsonResponse({"result": html_select, "value": int(request.GET.get("category_id"))})


class CreateFeatureView(View):
    def get(self, request, *args, **kwargs):
        category_id = request.GET.get("category_id")
        feature_name = request.GET.get("feature_name")
        value = request.GET.get("feature_value").strip(" ")
        category = Category.objects.get(id=int(category_id))
        feature = CategoryFeature.objects.get(category=category, feature_name=feature_name)
        existed_object, created = FeatureValidator.objects.get_or_create(
            category=category, feature_key=feature, valid_feature_value=value
        )
        if not created:
            return JsonResponse({"error": f"Значение '{value}' уже существует."})

        messages.add_message(
            request,
            messages.SUCCESS,
            f'Значение "{value}" для характеристики "{feature.feature_name}" '
            f'в категории "{category.name}" успешно создано',
        )
        return JsonResponse({"result": "OK"})


class NewProductFeatureView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        context = {"categories": categories}
        return render(request, "specs/new_product_feature.html", context)


class SearchProductAJAXView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("query")
        category_id = request.GET.get("category_id")
        category = Category.objects.get(id=int(category_id))
        products = list(Product.objects.filter(category=category, title__icontains=query).values())
        return JsonResponse({"result": products})


class AttachNewFeatureToProduct(View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.get(id=int(request.GET.get("product_id")))
        existing_features = list({item.feature.feature_name for item in product.features.all()})
        category_features = CategoryFeature.objects.filter(category=product.category).exclude(
            feature_name__in=existing_features
        )
        option = '<option value="{value}">{option_name}</option>'
        html_select = """
            <select class="form-select" name="product-category-features" id="product-category-features-id" aria-label="Default select example">
            <option selected>---</option>
            {result}
            </select>
        """
        result = "".join(
            option.format(value=item.category.id, option_name=item.feature_name) for item in category_features
        )

        html_select = html_select.format(result=result)
        return JsonResponse({"features": html_select})


class ProductFeatureChoicesAjaxView(View):
    def get(self, request, *args, **kwargs):
        category = Category.objects.get(id=int(request.GET.get("category_id")))
        feature_key = CategoryFeature.objects.get(
            category=category, feature_name=request.GET.get("product_feature_name")
        )
        validators_qs = FeatureValidator.objects.filter(category=category, feature_key=feature_key)
        option = '<option value="{value}">{option_name}</option>'
        html_select = """
                    <select class="form-select" name="product-category-features" id="product-category-features-id" aria-label="Default select example">
                    <option selected>---</option>
                    {result}
                    </select>
                """
        result = "".join(option.format(value=item.id, option_name=item.valid_feature_value) for item in validators_qs)

        html_select = html_select.format(result=result)
        return JsonResponse({"features": html_select})
