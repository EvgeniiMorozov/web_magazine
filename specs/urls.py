from django.urls import path

from specs.views import (
    BaseSpecView,
    CreateNewCategoryView,
    CreateNewFeatureView,
    CreateNewFeatureValidator,
    CreateFeatureView,
    FeatureChoiceView,
    NewProductFeatureView,
    SearchProductAJAXView,
    AttachNewFeatureToProduct,
    ProductFeatureChoicesAjaxView,
    CreateNewProductFeatureAJAXView,
    UpdateProductFeaturesView,
    ShowProductFeaturesforUpdate,
)

urlpatterns = [
    path("", BaseSpecView.as_view(), name="base-spec"),
    path("new-category/", CreateNewCategoryView.as_view(), name="new_category"),
    path("new-feature/", CreateNewFeatureView.as_view(), name="new_feature"),
    path("new-validator/", CreateNewFeatureValidator.as_view(), name="new_validator"),
    path("feature-choice/", FeatureChoiceView.as_view(), name="feature_choice"),
    path("feature-create/", CreateFeatureView.as_view(), name="create_feature"),
    path("new-product-feature/", NewProductFeatureView.as_view(), name="new_product_feature"),
    path("search-product/", SearchProductAJAXView.as_view(), name="search_product"),
    path("attach-feature/", AttachNewFeatureToProduct.as_view(), name="attach_feature"),
    path("product-feature/", ProductFeatureChoicesAjaxView.as_view(), name="product_feature"),
    path("create-new-product-feature/", CreateNewProductFeatureAJAXView.as_view(), name="product_feature"),
    path("update-product-features/", UpdateProductFeaturesView.as_view(), name="update_product_features"),
    path(
        "show-product-features-for-update/",
        ShowProductFeaturesforUpdate.as_view(),
        name="show_product_features_for_update",
    ),
]
