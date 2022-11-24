from django import forms

from .models import ProductAttribute

from .constants import CATEGORY_CHOICES, GENDERS, SIZES, COLORS


class FilterForm(forms.Form):
    """
    Simple form for filtered products
    """
    category = forms.CharField(max_length=255)
    size = forms.CharField(max_length=255)
    gender = forms.CharField(max_length=255)
    price = forms.CharField(max_length=255)


class ProductCreationForm(forms.Form):
    category = forms.ChoiceField(choices=CATEGORY_CHOICES)
    name = forms.CharField(max_length=150)
    description = forms.CharField(max_length=1024)
    main_image = forms.ImageField(required=False, initial='product_images/default/default_image.jpg')
    image1 = forms.ImageField(required=False, initial='product_images/default/dummy-product-image.png')
    image2 = forms.ImageField(required=False, initial='product_images/default/dummy-product-image.png')
    image3 = forms.ImageField(required=False, initial='product_images/default/dummy-product-image.png')
    image4 = forms.ImageField(required=False, initial='product_images/default/dummy-product-image.png')
    price = forms.FloatField()
    gender = forms.ChoiceField(choices=GENDERS)
    composition = forms.CharField(max_length=255)
    sizes = forms.MultipleChoiceField(choices=SIZES)
    colors = forms.MultipleChoiceField(choices=COLORS)

    def clean_name(self):
        # Check if product name already exist
        name = self.cleaned_data['name']
        try:
            name = ProductAttribute.objects.get(name=name)
        except ProductAttribute.DoesNotExist:
            return name
        raise forms.ValidationError(f'Product name {name} is already in use.')
