from django import forms
from django.forms import fields

from shop.models import Category


class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
