from collections import defaultdict

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView

from shop.models import Category, Product
from specs.forms import NewCategoryForm, NewCategoryFeatureKeyForm
from specs.models import CategoryFeature, FeatureValidator, ProductFeatures


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


class CreateNewProductFeatureAJAXView(View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.get(title=request.GET.get("product"))
        category_feature = CategoryFeature.objects.get(
            category=product.category, feature_name=request.GET.get("category_feature")
        )
        value = request.GET.get("value")
        feature = ProductFeatures.objects.create(feature=category_feature, product=product, value=value)
        product.features.add(feature)
        return JsonResponse({"OK": "OK"})


class UpdateProductFeaturesView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        context = {"categories": categories}
        return render(request, "specs/update_product_features.html", context)


class ShowProductFeaturesForUpdate(View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.get(id=int(request.GET.get("product_id")))
        features_values_qs = product.features.all()
        head = """
            <hr>
                <div class="row">
                    <div class="col-md-4">
                        <h4 class="text-center">Характеристика</h4>
                    </div>
                    <div class="col-md-4">
                        <h4 class="text-center">Текущее значение</h4>
                    </div>
                    <div class="col-md-4">
                        <h4 class="text-center">Новое значение</h4>
                    </div>
                </div>
            <div class="row">{}</div>
            <div class="row">
                <hr>
                <div class="col-md-4">
                </div>
                <div class="col-md-4">
                    <p class='text-center'><button class="btn btn-success" id="save-updated-features">Сохранить</button></p>
                </div>
                <div class="col-md-4">
                </div>
            </div>
        """
        option = "<option value='{value}'>{option_name}</option>"
        select_values = """
            <select class="form-select" name="feature-value" id="feature-value" aria-label="Default select example">
                <option selected>---</option>
                {result}
            </select>
        """
        mid_res = ""
        select_different_values_dict = defaultdict(list)

        for item in features_values_qs:
            fv_qs = FeatureValidator.objects.filter(category=item.product.category, feature_key=item.feature).values()
            for fv in fv_qs:
                if fv["valid_feature_value"] == item.value:
                    continue
                else:
                    select_different_values_dict[fv["feature_key_id"].append(fv["valid_feature_value"])]

            feature_field = "<input type='text' class='form-control' id='{id}' value='{value}' disabled/>"
            current_feature_value = """
                <div class="col-md-4 feature-current-value my-2">{}</div>
            """
            body_feature_field = """
                <div class="col-md-4 feature-name my-2">{}</div>
            """
            body_feature_field_value = """
                <div class="col-md-4 feature-new-value my-2">{}</div>
            """
            body_feature_field = body_feature_field.format(
                feature_field.format(id=item.feature.id, value=item.feature.feature_name)
            )

            current_feature_value_mid_res = "".join(
                option.format(value=item.feature.id, option_name=element)
                for element in select_different_values_dict[item.feature.id]
            )

            body_feature_field_value = body_feature_field_value.format(
                select_values.format(item.feature.id, result=current_feature_value_mid_res)
            )

            current_feature_value = current_feature_value.format(
                feature_field.format(id=item.feature.id, value=item.value)
            )

            data = body_feature_field + current_feature_value + body_feature_field_value
            mid_res += data

        result = head.format(mid_res)
        return JsonResponse({"result": result})


class UpdateProductFeaturesAJAXView(View):
    def post(self, request, *args, **kwargs):
        features_names = request.POST.getlist("features_names")
        features_current_values = request.POST.getlist("features_current_values")
        new_features_values = request.POST.getlist("new_features_values")

        data_for_update = [
            {"feature_name": name, "current_value": curr_value, "new_value": new_value}
            for name, curr_value, new_value in zip(features_names, features_current_values, new_features_values)
        ]

        product = Product.objects.get(title=request.POST.get("product"))

        for item in product.features.all():
            for item_for_update in data_for_update:
                if (
                        item.feature.feature_name == item_for_update["feature_name"]
                        and item.value != item_for_update["new_value"]
                        and item_for_update["new_value"] != "---"
                ):
                    cf = CategoryFeature.objects.get(
                        category=product.category, feature_name=item_for_update["feature_name"]
                    )
                    item.value = FeatureValidator.objects.get(
                        category=product.category, feture_key=cf, valid_feature_value=item_for_update["new_value"]
                    ).valid_feature_value

                    item.save()

        messages.add_message(
            request, messages.SUCCESS, f"Значения характеристик для товара {product.title} успешно обновлены"
        )
        return JsonResponse({"result": "ok"})
