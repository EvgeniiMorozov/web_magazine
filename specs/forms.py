from django import forms
from django.forms import fields

from shop.models import Category
from specs.models import CategoryFeature


class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class NewCategoryFeatureKeyForm(forms.ModelForm):
    class Meta:
        model = CategoryFeature
        fields = "__all__"
