from django.db import models


def recalculate_cart(cart):
    cart_data = cart.products.aggregate(models.Sum("final_price"), models.Count("id"))
    if not cart_data.get("final_price__sum"):
        cart.final_price = 0
    cart.final_price = cart_data["final_price__sum"]
    cart.total_products = cart_data["id__count"]
    cart.save()
