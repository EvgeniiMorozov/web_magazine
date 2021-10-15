from django.urls import path

from specs.views import (
    BaseSpecView,
    CreateNewCategoryView,
    CreateNewFeatureView,
    CreateNewFeatureValidator,
    FeatureChoiceView,
)


urlpatterns = [
    path("", BaseSpecView.as_view(), name="base-spec"),
    path("new-category/", CreateNewCategoryView.as_view(), name="new_category"),
    path("new-feature/", CreateNewFeatureView.as_view(), name="new_feature"),
    path("new-validator/", CreateNewFeatureValidator.as_view(), name="new_validator"),
    path("feature-choice/", FeatureChoiceView.as_view(), name="feature_choice"),
]
