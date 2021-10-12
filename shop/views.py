from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import DetailView, View

from shop.forms import OrderForm
from shop.mixins import CategoryDetailMixin, CartMixin
from shop.models import Notebook, Smartphone, Category, LatestProducts, CartProduct


class BaseView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        products = LatestProducts.objects.get_products_for_main_page(
            "notebook", "smartphone", with_respect_to="smartphone"
        )
        context = {"categories": categories, "products": products, "cart": self.cart}
        return render(request, "shop/base.html", context)


# def test_view(request):
#     categories = Category.objects.get_categories_for_left_sidebar()
#     return render(request, "shop/base.html", {"categories": categories})


class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):
    CT_MODEL_MODEL_CLASS = {"notebook": Notebook, "smartphone": Smartphone}

    context_object_name = "product"
    template_name = "shop/product_detail.html"
    slug_url_kwarg = "slug"

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs["ct_model"]]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ct_model"] = self.model._meta.model_name
        context["cart"] = self.cart
        return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
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
        ct_model, product_slug = kwargs.get("ct_model"), kwargs.get("slug")
        # customer = Customer.objects.get(user=request.user)
        # cart = Cart.objects.get(owner=customer, in_order=False)
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        if created:
            self.cart.products.add(cart_product)
        self.cart.save()
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        return HttpResponseRedirect("/cart/")


class DeleteFromCartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get("ct_model"), kwargs.get("slug")
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        self.cart.save()
        messages.add_message(request, messages.INFO, "Товар успешно удалён")
        return HttpResponseRedirect("/cart/")


class ChangeQTYView(CartMixin, View):
    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get("ct_model"), kwargs.get("slug")
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        qty = int(request.POST.get("qty"))
        cart_product.qty = qty
        cart_product.save()
        self.cart.save()
        messages.add_message(request, messages.INFO, "Кол-во успешно изменено")
        return HttpResponseRedirect("/cart/")


class CartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        context = {"cart": self.cart, "categories": categories}
        return render(request, "shop/cart.html", context)


class CheckoutView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        form = OrderForm(request.POST or None)
        context = {"cart": self.cart, "categories": categories, "form": form}
        return render(request, "shop/checkout.html", context)
