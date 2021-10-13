from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import DetailView, View

from shop.forms import OrderForm, LoginForm, RegistrationForm
from shop.mixins import CartMixin
from shop.models import Category, CartProduct, Customer, Product
from shop.utils import recalculate_cart


class BaseView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        products = Product.objects.all()
        context = {"categories": categories, "products": products, "cart": self.cart}
        return render(request, "shop/base.html", context)


class ProductDetailView(CartMixin, DetailView):
    context_object_name = "product"
    template_name = "shop/product_detail.html"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = self.cart
        return context


class CategoryDetailView(CartMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = "categories"
    template_name = "shop/category_detail.html"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = self.cart
        return context


class AddToCartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get("slug")
        product = Product.objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(user=self.cart.owner, cart=self.cart, product=product)
        if created:
            self.cart.products.add(cart_product)
        recalculate_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        return HttpResponseRedirect("/cart/")


class DeleteFromCartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get("slug")
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(user=self.cart.owner, cart=self.cart, product=product)
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalculate_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно удалён")
        return HttpResponseRedirect("/cart/")


class ChangeQTYView(CartMixin, View):
    def post(self, request, *args, **kwargs):
        product_slug = kwargs.get("slug")
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(user=self.cart.owner, cart=self.cart, product=product)
        qty = int(request.POST.get("qty"))
        cart_product.qty = qty
        cart_product.save()
        recalculate_cart(self.cart)
        messages.add_message(request, messages.INFO, "Кол-во успешно изменено")
        return HttpResponseRedirect("/cart/")


class CartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        context = {"cart": self.cart, "categories": categories}
        return render(request, "shop/cart.html", context)


class CheckoutView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        form = OrderForm(request.POST or None)
        print(request.POST)
        context = {"cart": self.cart, "categories": categories, "form": form}
        return render(request, "shop/checkout.html", context)


class MakeOrderView(CartMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data["first_name"]
            new_order.last_name = form.cleaned_data["last_name"]
            new_order.phone = form.cleaned_data["phone"]
            new_order.address = form.cleaned_data["address"]
            new_order.buying_type = form.cleaned_data["buying_type"]
            new_order.order_date = form.cleaned_data["order_date"]
            new_order.comment = form.cleaned_data["comment"]
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, "Спасибо за заказ! Мы с Вами свяжемся!")
            return HttpResponseRedirect("/")
        return HttpResponseRedirect("/checkout/")


class LoginView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        categories = Category.objects.all()
        context = {"form": form, "categories": categories, "cart": self.cart}
        return render(request, "shop/login.html", context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect("/")

        context = {"form": form, "cart": self.cart}
        return render(request, "shop/login.html", context)


class RegistrationView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        categories = Category.objects.all()
        context = {"form": form, "categories": categories, "cart": self.cart}
        return render(request, "shop/registration.html", context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data["username"]
            new_user.email = form.cleaned_data["email"]
            new_user.first_name = form.cleaned_data["first_name"]
            new_user.last_name = form.cleaned_data["last_name"]
            new_user.save()
            new_user.set_password(form.cleaned_data["password"])
            new_user.save()
            Customer.objects.create(
                user=new_user, phone=form.cleaned_data["phone"], address=form.cleaned_data["address"]
            )
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            login(request, user)
            return HttpResponseRedirect("/")

        context = {"form": form, "cart": self.cart}
        return render(request, "shop/registration.html", context)
