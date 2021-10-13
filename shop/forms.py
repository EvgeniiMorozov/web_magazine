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


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password", "confirm_password", "first_name", "last_name", "phone", "address")

    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(required=False)
    address = forms.CharField(required=False)
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["password"].label = "Пароль"
        self.fields["confirm_password"].label = "Подтвердите пароль"
        self.fields["phone"].label = "Номер телефона"
        self.fields["address"].label = "Адрес"
        self.fields["email"].label = "Электронная почта"
        self.fields["first_name"].label = "Ваше имя"
        self.fields["last_name"].label = "Ваша фамилия"

    def clean_email(self):
        email = self.cleaned_data["email"]
        domain = email.split(".")[-1]

        if domain in ["com", "net"]:
            raise forms.ValidationError(f"Регистрация для домена '{domain}' не возможна")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f"Данный почтовый адрес {email} уже зарегестрирован")

        return email

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"Имя {username} занято")

        return username

    def clean(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]

        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")

        return self.cleaned_data
