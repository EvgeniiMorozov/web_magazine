from django.contrib import admin

from shop.models import Category, Customer, Cart, CartProduct, Order, Product

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Order)
admin.site.register(Product)
