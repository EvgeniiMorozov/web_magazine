from django.urls import path

from specs.views import BaseSpecView, NewCategoryView


urlpatterns = [
    path("", BaseSpecView.as_view(), name="base-spec"),
    path("new-category/", NewCategoryView.as_view(), name="new_category"),
]
