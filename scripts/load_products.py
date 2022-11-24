import csv
from product.models import ProductAttribute, Product, Color, Size


def run():
    """
    Script to create plenty of database objects to work with
    """
    # Create colours
    Color.objects.create(color='Blue')
    Color.objects.create(color='Red')
    Color.objects.create(color='Green')
    Color.objects.create(color='Yellow')

    blue = Color.objects.get(color='Blue')
    red = Color.objects.get(color='Red')
    green = Color.objects.get(color='Green')
    yellow = Color.objects.get(color='Yellow')

    # Create sizes
    Size.objects.create(size='S')
    Size.objects.create(size='M')
    Size.objects.create(size='L')
    Size.objects.create(size='XL')
    Size.objects.create(size='XXL')

    s = Size.objects.get(size='S')
    m = Size.objects.get(size='M')
    l = Size.objects.get(size='L')
    xl = Size.objects.get(size='XL')
    xxl = Size.objects.get(size='XXL')

    with open('scripts/clothes.csv') as file:
        reader = csv.reader(file)

        for row in reader:
            prop = row[0].split(';')
            print(prop)
            # Create product attributes object
            attributes = ProductAttribute.objects.create(category=prop[0], name=prop[1], description=prop[2], price=prop[3], gender=prop[4], composition=prop[5])

            # Create product object
            product = Product.objects.create(product=attributes)
            # Add colours and sizes
            product.sizes.add(s)
            product.sizes.add(m)
            product.sizes.add(l)
            product.sizes.add(xl)
            product.sizes.add(xxl)
            product.colors.add(blue)
            product.colors.add(red)
            product.colors.add(green)
            product.colors.add(yellow)
            product.save()
