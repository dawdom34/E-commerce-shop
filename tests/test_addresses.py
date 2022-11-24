from django.urls import reverse
from django.test import TestCase

from account.models import Account, Address, Cart
from account.forms import AddressForm
from product.models import Product, ProductAttribute, Color, Size


class BaseTest(TestCase):
    def setUp(self):
        # Create user
        self.user = Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email="examplenew@gmail.com", gender='Man', phone_number='32111222333', password='ExamplePassword123')
        # Create other user
        self.other_user = Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='example@gmail.com', gender='Man', phone_number='32199222333', password='ExamplePassword123')
        # Create address
        self.address1 = Address.objects.create(address1='address1', address2='address2', zip_code='12-345', city='Berlin', country='Germany', user=self.user)
        # Address data form valid
        self.address_valid = {'address1': 'address', 'address2': 'address', 'zip_code': '12-545', 'city': 'Berlin', 'country': 'Germany'}
        # Address data form invalid
        self.address_invalid = {'address1': 'address3', 'address2': 'address3', 'zip_code': '12-347', 'city': 'Berlin', 'country': 'abcde'}
        # Addresses data form
        self.address2 = {'address1': 'abc', 'address2': 'abc', 'zip_code': '11-111', 'city': 'Berlin', 'country': 'Germany'}
        self.address3 = {'address1': 'abcd', 'address2': 'abcd', 'zip_code': '11-112', 'city': 'Berlin', 'country': 'Germany'}
        self.address4 = {'address1': 'abcde', 'address2': 'abcde', 'zip_code': '11-113', 'city': 'Berlin', 'country': 'Germany'}
        self.address5 = {'address1': 'abcdef', 'address2': 'abcdef', 'zip_code': '11-115', 'city': 'Berlin', 'country': 'Germany'}
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
        # Login data
        self.user_auth = {'email': 'examplenew@gmail.com', 'password': 'ExamplePassword123'}
        # json data
        self.data = {'address_id': self.address1.id}
        # URLS
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.address_add = reverse('account:address', kwargs={'user_id': self.user.id})
        self.address_delete = reverse('account:remove_address')
        return super().setUp()


class AddressesTest(BaseTest):
    def test_address_add(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.address_add)
        response2 = self.client.post(self.address_add, self.address_valid)
        # Check for status code, success
        self.assertEqual(response.status_code, 200)
        # Check for status code, redirect
        self.assertEqual(response2.status_code, 302)
        # Check template
        self.assertTemplateUsed(response, 'account/address.html')

    def test_address_add_view_when_user_is_not_authenticated(self):
        response = self.client.get(self.address_add)
        # Check for status code, redirect
        self.assertEqual(response.status_code, 302)

    def test_address_add_view_when_user_id_is_not_valid(self):
        """
        Test if user is trying to see his own profile or if user id does not exist
        """
        # User not exist
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.new_address_url = reverse('account:address', kwargs={'user_id': 123})
        # GET
        response = self.client.get(self.new_address_url)
        self.assertEqual(response.content, b'That user does not exist')
        # POST
        response2 = self.client.post(self.new_address_url, self.address_valid)
        self.assertEqual(response2.content, b'That user does not exist')

        # User is trying to see someone else profile
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.new_address_url = reverse('account:address', kwargs={'user_id': self.other_user.id})
        # GET
        response = self.client.get(self.new_address_url)
        self.assertEqual(response.content, b'You cannot see other user addresses')
        # POST
        response2 = self.client.post(self.new_address_url, self.address_valid)
        self.assertEqual(response2.content, b'You cannot see other user addresses')

    def test_address_view_when_address_is_not_valid(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.address_add, self.address_invalid)
        self.assertEqual(response.status_code, 401)

    def test_address_form_when_user_have_already_4_addresses(self):
        """
        Test if user can only have 4 addresses
        """
        self.client.post(self.login_url, self.user_auth, format='text/html')
        # Add 3 more addresses
        self.client.post(self.address_add, self.address2)
        self.client.post(self.address_add, self.address3)
        self.client.post(self.address_add, self.address4)
        # Try to add 5th address
        form = AddressForm(self.user, data=self.address5)
        self.assertEqual(form.errors, {'__all__': ['You can only have 4 addresses']})

    def test_address_form_if_address_already_exist(self):
        """
        Test if user can add address if same address already exist
        """
        self.client.post(self.login_url, self.user_auth, format='text/html')
        form = AddressForm(self.user, data={'address1': 'address1', 'address2': 'address2', 'zip_code': '12-345', 'city': 'Berlin', 'country': 'Germany'})
        self.assertEqual(form.errors, {'__all__': ['You already have this address']})

    def test_address_form_if_country_does_not_exist(self):
        """
        Test if user can add address with not existing country
        """
        self.client.post(self.login_url, self.user_auth, format='text/html')
        form = AddressForm(self.user, data=self.address_invalid)
        self.assertEqual(form.errors, {'__all__': ["That country doesn't exist"]})

    def test_delete_address(self):
        """
        Test address delete
        """
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.address_delete, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Address deleted."}')

    def test_delete_address_when_user_in_not_authenticated(self):
        response = self.client.post(self.address_delete, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "You must be authenticated to delete this address"}')

    def test_delete_address_with_invalid_id(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.address_delete, {'address_id': 123}, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "Unable to delete this address."}')
