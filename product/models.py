from django.conf import settings
from django.db import models

from .constants import CATEGORY_CHOICES, GENDERS, SIZES, COLORS, SCORES


def main_image_filepath(self, *args, **kwargs):  # pragma: no cover
    return f'product_images/{str(self.id)}/main_image.jpg'


def images_filepath(self, *args, **kwargs):  # pragma: no cover
    return f'product_images/{str(self.id)}/images.jpg'


def default_main_image_filepath(*args, **kwargs):  # pragma: no cover
    return 'product_images/default/default_image.jpg'


def default_image_filepath(*args, **kwargs):  # pragma: no cover
    return 'product_images/default/dummy-product-image.png'


class ProductAttribute(models.Model):
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True)
    main_image = models.ImageField(upload_to=main_image_filepath, null=True, blank=True,
                                   default=default_main_image_filepath)
    image1 = models.ImageField(upload_to=images_filepath, default=default_image_filepath, null=True, blank=True)
    image2 = models.ImageField(upload_to=images_filepath, default=default_image_filepath, null=True, blank=True)
    image3 = models.ImageField(upload_to=images_filepath, default=default_image_filepath, null=True, blank=True)
    image4 = models.ImageField(upload_to=images_filepath, default=default_image_filepath, null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    gender = models.CharField(max_length=10, choices=GENDERS)
    composition = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class Size(models.Model):
    size = models.CharField(max_length=5, choices=SIZES, verbose_name='size')

    def __str__(self):
        return f'{self.size}'


class Color(models.Model):
    color = models.CharField(max_length=20, choices=COLORS, verbose_name='color')

    def __str__(self):
        return f'{self.color}'


class Product(models.Model):
    product = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='product_attrs')
    sizes = models.ManyToManyField(Size, related_name='sizes', blank=True)
    colors = models.ManyToManyField(Color, related_name='colors', blank=True)

    def __str__(self):
        return f'{self.product}'


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.SmallIntegerField(choices=SCORES, blank=False, null=False)
    review = models.TextField(verbose_name='review', max_length=1024, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
