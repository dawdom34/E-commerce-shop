from django.test import TestCase
from django.urls import reverse

from account.models import Account, Cart, CartItem
from product.models import Product, ProductAttribute, Size, Color


class BaseTest(TestCase):
    def setUp(self):
        # URLS
        self.login_url = reverse('login')
        # Create users
        self.user = Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='ExampleNEw@gmail.com', gender='Man', phone_number='32111222333', password='ExamplePassword123')
        self.other_user = Account.objects.create_user(name='ExampleOtherName', surname='ExampleOtherSurname', email='ExampleOther@gmail.com', gender='Man', phone_number='32113222333', password='ExamplePassword123')
        # Create product
        self.prod_attr = ProductAttribute.objects.create(
            category='T-shirt',
            name='Product name',
            description='Product Description',
            price=100,
            gender='Man',
            composition='Cotton'
        )
        # Create color
        c = Color.objects.create(color='Red')
        c.save()
        self.color = Color.objects.get(color='Red')
        # Create size
        s = Size.objects.create(size='L')
        s.save()
        self.size = Size.objects.get(size='L')
        # Create product
        self.product = Product.objects.create(product=self.prod_attr)
        self.product.save()
        self.product.sizes.add(self.size)
        self.product.colors.add(self.color)
        # Create cart item
        self.cart_item = CartItem.objects.create(
            product=self.product,
            quantity=2,
            color=self.color,
            size=self.size,
            user=self.user,
            is_active=True
        )
        # Add product to cart
        self.cart = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart.add_product(self.product, 2, self.color, self.size, self.user)
        return super().setUp()


class ProfileViewTest(BaseTest):
    def test_profile_view_with_cart_complete(self):
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.profile_view_url = reverse('account:view', kwargs={'user_id': self.user.id})
        self.cart.mark_as_complete()
        self.new_cart = Cart.objects.get(user=self.user, transaction_completed=False)
        self.new_cart.add_product(self.product, 2, self.color, self.size, self.user)
        response = self.client.get(self.profile_view_url)
        self.assertEqual(response.status_code, 200)

    def test_profile_view_with_cart_incomplete(self):
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.profile_view_url = reverse('account:view', kwargs={'user_id': self.user.id})
        response = self.client.get(self.profile_view_url)
        self.assertEqual(response.status_code, 200)

    def test_profile_view_when_user_is_not_authenticated(self):
        self.profile_view_url = reverse('account:view', kwargs={'user_id': self.user.id})
        response = self.client.get(self.profile_view_url)
        self.assertEqual(response.status_code, 302)

    def test_profile_view_when_user_trying_to_see_someone_else_profile(self):
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.profile_view_url = reverse('account:view', kwargs={'user_id': self.other_user.id})
        response = self.client.get(self.profile_view_url)
        self.assertEqual(response.content, b'You cannot see other user profile')

    def test_profile_view_when_user_id_does_not_exist(self):
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.profile_view_url = reverse('account:view', kwargs={'user_id': 1111})
        response = self.client.get(self.profile_view_url)
        self.assertEqual(response.content, b"That user doesn't exist.")
