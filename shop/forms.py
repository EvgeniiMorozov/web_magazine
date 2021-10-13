from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from shop.models import Order


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order_date"].label = "Дата получения заказа"

    order_date = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    # comment = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        model = Order
        fields = ("first_name", "last_name", "phone", "address", "buying_type", "order_date", "comment")


class LoginForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "password"]

    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["password"].label = "Пароль"

    def clean(self):
        # super().clean()
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]

        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"Пользователь с логином {username} не найден в системе")

        user = User.objects.filter(username=username).first()

        if user and not user.check_password(password):
            raise forms.ValidationError("Введён неверный пароль")

        return self.cleaned_data
