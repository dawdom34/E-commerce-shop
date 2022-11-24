from django.test import TestCase
from django.urls import reverse

from account.models import Account, Cart
from account.forms import AccountEditForm
from product.models import Product, ProductAttribute, Color, Size


class BaseTest(TestCase):
    def setUp(self):
        # Create user
        self.user = Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='examplenew@gmail.com', gender='Man', phone_number='32111222333', password='ExamplePassword123')
        # Create other user
        self.other_user = Account.objects.create_user(name='Example', surname='ExampleSurname', email='example@gmail.com', gender='Man', phone_number='32111772333', password='ExamplePassword123')
        # Login data
        self.user_auth = {'email': 'examplenew@gmail.com', 'password': 'ExamplePassword123'}
        # New valid user data
        self.valid_data = {'name': 'NewName', 'surname': 'New Surname', 'email': 'NewEmail@gmail.com', 'phone_number': '11123123123'}
        # New invalid user data
        self.invalid_data = {'name': 'NewName', 'surname': 'New Surname', 'email': 'NewEmail', 'phone_number': '11123123123'}
        # Create product
        self.prod_attr = ProductAttribute.objects.create(
            category='T-shirts',
            name='Product name',
            description='Product Description',
            main_image='product_images/default/default_image.jpg',
            image1='product_images/default/default_image.jpg',
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
        # Add product to cart
        self.cart = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart.add_product(self.product, 4, self.color, self.size, self.user)
        # Account edit url
        self.edit_account_url = reverse('account:edit_profile', kwargs={'user_id': self.user.id})
        # Login url
        self.login_url = reverse('login')
        return super().setUp()


class TestUserProfileEdit(BaseTest):
    def test_profile_edit_get(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.edit_account_url)
        # Check for status code and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('account/profile_edit.html')

    def test_profile_edit_when_user_is_not_authenticated(self):
        response = self.client.get(self.edit_account_url)
        # Check for status code(redirect)
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_when_user_id_does_not_exist(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        # Define new url
        self.new_account_edit_url = reverse('account:edit_profile', kwargs={'user_id': 123})
        response = self.client.get(self.new_account_edit_url)
        self.assertEqual(response.content, b'User does not exist')

    def test_profile_edit_when_user_id_is_not_valid(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        # Define new url
        self.new_account_edit_url = reverse('account:edit_profile', kwargs={'user_id': self.other_user.id})
        response = self.client.get(self.new_account_edit_url)
        self.assertEqual(response.content, b'You cannot edit someone else profile')

    def test_profile_edit_with_valid_data(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.edit_account_url, self.valid_data)
        # Check for status code(redirect)
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_with_invalid_data(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.edit_account_url, self.invalid_data)
        # Check for status code
        self.assertEqual(response.status_code, 401)

    def test_profile_edit_form_with_invalid_email(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        # Define new invalid data
        self.invalid_email = {'name': 'NewName', 'surname': 'NewSurname', 'email': 'example@gmail.com', 'phone_number': '12999888777'}
        form = AccountEditForm(self.invalid_email)
        self.assertEqual(form.errors, {'email': ["Email example@gmail.com is already in use."]})

    def test_profile_edit_form_with_invalid_phone_number(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        # Define new invalid data
        self.invalid_number = {'name': 'NewName', 'surname': 'NewSurname', 'email': 'exampleeet@gmail.com', 'phone_number': '32111772333'}
        form = AccountEditForm(data=self.invalid_number)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'phone_number': ["Phone number 32111772333 is already in use."]})
