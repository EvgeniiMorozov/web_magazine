from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory

from shop.models import Category, Notebook, Cart, CartProduct, Customer
from shop.utils import recalculate_cart
from shop.views import AddToCartView

User = get_user_model()


class ShopTestCases(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username="test-user", password="password")
        self.category = Category.objects.create(name="Ноутбуки", slug="notebooks")
        image = SimpleUploadedFile("notebook_image.jpg", content=b"", content_type="image/jpg")
        self.notebook = Notebook.objects.create(
            category=self.category,
            title="test_notebook",
            slug="test-slug",
            image=image,
            price=Decimal("50000.00"),
            diagonal='17.3"',
            display="IPS",
            cpu="Test Intel",
            ram="8 ГБ",
            video="NVidia",
        )
        self.customer = Customer.objects.create(user=self.user, phone="1212121212", address="Test Address")
        self.cart = Cart.objects.create(owner=self.customer)
        self.cart_product = CartProduct.objects.create(user=self.customer, cart=self.cart, content_object=self.notebook)

    def test_add_to_cart(self):
        self.cart.products.add(self.cart_product)
        recalculate_cart(self.cart)
        self.assertIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 1)
        self.assertEqual(self.cart.final_price, Decimal("50000.00"))

    def test_response_from_add_to_cart_view(self):
        # client = Client()
        # response = client.get("/add-to-cart/notebook/test-slug")
        # self.assertEqual(response.status_code, 200)
        factory = RequestFactory()
        request = factory.get("")
        request.user = self.user
        response = AddToCartView.as_view()(request, ct_model="notebook", slug="test-slug")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/cart/")
