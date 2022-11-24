from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver

from product.models import Product
from coupons.models import Coupon


class AccountManager(BaseUserManager):
    def create_user(self, email, name, surname, gender, phone_number, password=None):
        if not email:
            raise ValueError('Users must have an email address.')
        if not name:
            raise ValueError('Users must have a name.')
        if not surname:
            raise ValueError('Users must have surname.')
        if not gender:
            raise ValueError('Users must have a gender')
        if gender not in ['Man', 'Woman']:
            raise ValueError('Invalid gender.')
        if not phone_number:
            raise ValueError('Users must have a phone number.')
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            surname=surname,
            gender=gender,
            phone_number=phone_number
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, gender, phone_number, password):
        user = self.create_user(
            email=self.normalize_email(email),
            name=name,
            surname=surname,
            gender=gender,
            phone_number=phone_number,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    GENDERS = (
        ('Man', 'Man'),
        ('Woman', 'Woman')
    )

    email = models.EmailField(verbose_name='Email', max_length=60, unique=True)
    name = models.TextField(verbose_name='Name', max_length=50)
    surname = models.TextField(verbose_name='Surname', max_length=80)
    phone_number = models.TextField(null=True, blank=True, unique=True, verbose_name='Phone number')
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    gender = models.CharField(verbose_name='gender', max_length=7, choices=GENDERS)
    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'gender', 'phone_number']

    def __str__(self):
        return f'{self.name} {self.surname}'

    def has_perm(self, perm):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


@receiver(post_save, sender=Account)
def create_cart(sender, instance, **kwargs):
    """
    Create cart object after saving a new user
    """
    Cart.objects.get_or_create(user=instance, transaction_completed=False)


class Address(models.Model):
    address1 = models.CharField(verbose_name='address1', max_length=1024)
    address2 = models.CharField(verbose_name='address2', max_length=1024, null=True, blank=True)
    zip_code = models.CharField(verbose_name='zip code', max_length=20)
    city = models.CharField(verbose_name='city', max_length=100)
    country = models.CharField(verbose_name='country', max_length=200)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(verbose_name='quantity')
    color = models.CharField(max_length=50, default='White')
    size = models.CharField(max_length=5, default='M')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.product)

    def increment_quantity(self, new_quantity):
        """
        Add new quantity if the same product is already in cart
        """
        old_quantity = int(self.quantity)
        self.quantity = old_quantity + int(new_quantity)


class Cart(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    products = models.ManyToManyField(CartItem, related_name='products', blank=True)
    transaction_completed = models.BooleanField(default=False)
    timestamp = models.DateField(blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.user.name} {self.user.surname} {self.transaction_completed}'

    def add_product(self, product, quantity, color, size, user):
        """
        Add a new product to cart or increment it quantity
        """
        try:
            item = CartItem.objects.get(product=product, color=color, size=size, user=user, is_active=True)
            item.increment_quantity(quantity)
            item.save()
        except CartItem.DoesNotExist:
            self.products.add(CartItem.objects.create(product=product, quantity=quantity, color=color, size=size, user=user))

    def delete_product(self, product_id):
        """
        Delete product from cart
        """
        instance = CartItem.objects.get(id=product_id)
        instance.delete()

    def mark_as_complete(self):
        """
        Mark the transaction as complete
        """
        for product in self.products.all():
            product.is_active = False
            product.save()

        self.transaction_completed = True
        self.timestamp = date.today()
        # Create status object
        OrderStatus.objects.create(order=self, status='Collecting an items')
        # Create new empty cart for authenticated user
        Cart.objects.create(user=self.user)
        self.save()

    def add_address(self, address_id):
        """
        Add delivery address to cart
        """
        address = Address.objects.get(id=address_id)
        self.address = address
        self.save()

    def add_coupon(self, coupon):
        """
        Add a coupon
        """
        self.coupon = coupon
        coupon.counter_increment()
        coupon.save()
        self.save()

    def delete_coupon(self):
        """
        Delete coupon
        """
        self.coupon = None
        self.save()


class OrderStatus(models.Model):

    STATUS_CHOICES = (
        ('Collecting an items', 'Collecting an items'),
        ('Waiting for shipment', 'Waiting for shipment'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    )

    order = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, verbose_name='status', max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
