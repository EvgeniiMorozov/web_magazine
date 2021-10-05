from PIL import Image
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

User = get_user_model()


def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


def get_product_url(obj, view_name):
    ct_model = obj.__class__._meta.model_name
    return reverse(view_name, kwargs={"ct_model": ct_model, "slug": obj.slug})


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class LatestProductsManager:
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get("with_respect_to")
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by("-id")[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists() and with_respect_to in args:
                return sorted(
                    products,
                    key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to),
                    reverse=True,
                )
        return products


class LatestProducts:
    objects = LatestProductsManager()


# class CategoryManager(models.Manager):

#     CATEGORY_NAME_COUNT_NAME = {"Ноутбуки": "notebook__count", "Смартфоны": "smartphone__count"}

#     def get_queryset(self):
#         return super().get_queryset()

#     def get_categories_for_lef_sidebar(self):
#         models = get_models_for_count("notebook", "smartphone")
#         qs = list(self.get_queryset().annotate(*models))

#         return [
#             dict(
#                 name=c.name,
#                 url=c.get_absolute_url(),
#                 count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]),
#             )
#             for c in qs
#         ]


class CategoryManager(models.Manager):

    CATEGORY_NAME_COUNT_NAME = {"Ноутбуки": "notebook__count", "Смартфоны": "smartphone__count"}

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_left_sidebar(self):
        models = get_models_for_count("notebook", "smartphone")
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя Категории")
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})


class Product(models.Model):
    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (800, 800)
    MAX_IMAGE_SIZE = 3145728

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Наименование")
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name="Изображение")
    description = models.TextField(verbose_name="Описание", null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Цена")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        img_height, img_width = img.size
        min_height, min_width = self.MIN_RESOLUTION
        max_height, max_width = self.MAX_RESOLUTION

        # Проверка загружаемого изображения на минимальное и максимальное разрешение
        if img_height < min_height or img_width < min_width:
            raise MinResolutionErrorException("Разрешение изображения меньше минимального!")
        if img_height > max_height or img_width > max_width:
            raise MaxResolutionErrorException("Разрешение изображения больше максимального!")

        # # Принудительное форматирование изображения
        # image = self.image
        # img = Image.open(image)
        # # Убираем альфа-канал (RGBA -> RGB)
        # new_img = img.convert("RGB")
        # resized_mew_img = new_img.resize(self.MAX_RESOLUTION, Image.ANTIALIAS)
        # file_stream = BytesIO()
        # resized_mew_img.save(file_stream, "JPEG", quality=90)
        # file_stream.seek(0)
        # name = "{}.{}".format(*self.image.name.split("."))
        # self.image = InMemoryUploadedFile(
        #     file_stream, "ImageField", name, "image/jpeg", sys.getsizeof(file_stream), None
        # )

        super().save(*args, **kwargs)


class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name="Диагональ экрана")
    display = models.CharField(max_length=255, verbose_name="Тип дисплея")
    cpu = models.CharField(max_length=255, verbose_name="Процессор")
    ram = models.CharField(max_length=255, verbose_name="Оперативная память")
    video = models.CharField(max_length=255, verbose_name="Видеокарта")

    def __str__(self):
        return f"{self.category.name} : {self.title}"

    def get_absolute_url(self):
        return get_product_url(self, "product_detail")


class Smartphone(Product):
    diagonal = models.CharField(max_length=255, verbose_name="Диагональ экрана")
    display = models.CharField(max_length=255, verbose_name="Тип дисплея")
    resolution = models.CharField(max_length=255, verbose_name="Разрешение экрана")
    batt_capacity = models.CharField(max_length=255, verbose_name="Объем батареи")
    ram = models.CharField(max_length=255, verbose_name="Оперативная память")
    rom = models.CharField(max_length=255, verbose_name="Встроенная память")
    main_cam_mp = models.CharField(max_length=255, verbose_name="Разрешение основной камеры")

    def __str__(self):
        return f"{self.category.name} : {self.title}"

    def get_absolute_url(self):
        return get_product_url(self, "product_detail")


class CartProduct(models.Model):
    user = models.ForeignKey("Customer", verbose_name="Покупатель", on_delete=models.CASCADE)
    cart = models.ForeignKey(
        "Cart",
        verbose_name="Корзина",
        on_delete=models.CASCADE,
        related_name="related_products",
    )
    # product = models.ForeignKey(Product, verbose_name="Продукт", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Общая цена")

    def __str__(self):
        return f"Продукт: {self.content_object.title} (для корзины)"


class Cart(models.Model):
    owner = models.ForeignKey("Customer", verbose_name="Владелец", on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name="related_cart")
    # total_products - чтоб показывать корректное количество товаров в корзине
    # 2 смартфона и 3 ноутбука - 2 разных продукта и 5 товаров
    total_products = models.PositiveIntegerField(default=0)

    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Общая цена")
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name="Покупатель", on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name="Номер телефона")
    address = models.CharField(max_length=255, verbose_name="Адрес")

    def __str__(self):
        return f"Покупатель: {self.user.first_name} {self.user.last_name}"


class Specification(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    title = models.CharField(max_length=255, verbose_name="Название товара для характеристик")

    def __str__(self):
        return f"Характеристики для товара: {self.title}"
