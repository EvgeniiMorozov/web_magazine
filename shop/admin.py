from django.contrib import admin

from shop.models import Category, Customer, Cart, CartProduct, Order, Product


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    change_form_template = "shop/custom_admin/change_form.html"


admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Order)
admin.site.register(Product, ProductAdmin)
