from django.test import TestCase
from django.urls import reverse

from account.models import Account, Cart, CartItem, Address
from product.models import Product, ProductAttribute, Size, Color
from coupons.models import Coupon


class BaseTest(TestCase):
    def setUp(self):
        # Create user
        self.user = Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='examplenew@gmail.com', gender='Man', phone_number='32111222333', password='ExamplePassword123')
        # Create other user
        self.other_user = Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='example@gmail.com', gender='Man', phone_number='32113212333', password='ExamplePassword123')
        # Login data
        self.auth = {'email': 'examplenew@gmail.com', 'password': 'ExamplePassword123'}
        self.auth_other_user = {'email': 'example@gmail.com', 'password': 'ExamplePassword123'}
        # Create product attributes
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
        # mark cart as complete
        self.cart.mark_as_complete()
        # Add another product to new cart
        self.cart2 = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart2.add_product(self.product, 2, self.color, self.size, self.user)
        # Create address
        self.address = Address.objects.create(address1='address1', address2='address2', zip_code='12-345', city='Berlin', country='Germany', user=self.user)
        # Create active coupon
        self.coupon = Coupon.objects.create(coupon='coupon', discount=15)
        # Create inactive coupon
        self.inactive_coupon = Coupon.objects.create(coupon='coupon2', discount=15, is_active=False, counter=0)
        # URLS
        self.login = reverse('login')
        self.cart_url = reverse('account:cart', kwargs={'user_id': self.user.id})
        self.add = reverse('account:cart_add_product')
        self.delete = reverse('account:cart_remove_product')
        self.orders = reverse('account:my_orders')
        self.details = reverse('account:order_details', kwargs={'order_id': self.cart2.id})
        # json data
        self.data = {'product_id': self.product.id, 'quantity': 2, 'color': self.color, 'size': self.size}
        self.invalid_data = {'product_id': 123, 'quantity': 2, 'color': self.color, 'size': self.size}
        self.invalid_data_delete = {'product_id': 123}
        return super().setUp()


class CartTest(BaseTest):
    def test_cart_view(self):
        self.client.post(self.login, self.auth_other_user, format='text/html')
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)

    def test_cart_view_when_user_not_auth(self):
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 302)

    def test_cart_view_when_user_id_not_exist(self):
        self.new_url = reverse('account:cart', kwargs={'user_id': 123})
        self.client.post(self.login, self.auth, format='text/html')
        response = self.client.get(self.new_url)
        self.assertEqual(response.content, b'Something went wrong')

    def test_cart_view_when_user_id_not_valid(self):
        self.new_url = reverse('account:cart', kwargs={'user_id': self.other_user.id})
        self.client.post(self.login, self.auth, format='text/html')
        response = self.client.get(self.new_url)
        self.assertEqual(response.content, b'You cannot see other users carts')

    def test_cart_view_when_active_coupon_applied(self):
        self.client.post(self.login, self.auth, format='text/html')
        self.cart_user = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart_user.add_coupon(self.coupon)
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)

    def test_cart_view_when_inactive_coupon_applied(self):
        self.client.post(self.login, self.auth, format='text/html')
        self.cart_user = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart_user.add_coupon(self.inactive_coupon)
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)

    def test_cart_view_add_address(self):
        self.client.post(self.login, self.auth, format='text/html')
        self.cart_user = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart_user.add_address(self.address.id)
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)

    def test_cart_view_add_product(self):
        self.client.post(self.login, self.auth, format='text/html')
        response = self.client.post(self.add, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Product added."}')

    def test_cart_view_add_prodct_when_product_does_not_exist(self):
        self.client.post(self.login, self.auth, format='text/html')
        response = self.client.post(self.add, self.invalid_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Unable to add this product."}')
    
    def test_cart_view_add_prodct_when_product_user_not_auth(self):
        response = self.client.post(self.add, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "You must be authenticated to add this product"}')

    def test_cart_model_add_and_delete_product(self):
        self.client.post(self.login, self.auth, format='text/html')
        self.cart_user = Cart.objects.get(user=self.user, transaction_completed=False)
        # Increment quantity
        self.cart_user.add_product(self.product, 1, self.color, self.size, self.user)
        # Add product
        self.cart_user.add_product(self.product, 1, self.color, self.size, self.user)
        self.cart_user.delete_product(self.product.id)

    def test_cart_model_mark_as_complete(self):
        self.client.post(self.login, self.auth, format='text/html')
        self.cart_user = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart_user.mark_as_complete()
        # Test cart str method
        self.assertEqual(str(self.cart_user), 'ExampleName ExampleSurname True')
        # Test cartitem str method
        self.assertEqual(str(self.cart_item), 'Product name')

    def test_cart_view_when_cart_does_not_exist(self):
        self.client.post(self.login, self.auth, format='text/html')
        self.cart_user = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart_user.delete()
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)

    def test_cart_view_remove_product(self):
        self.client.post(self.login, self.auth, format='text/html')
        response = self.client.post(self.delete, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Product deleted."}')

    def test_cart_view_remove_prodct_when_product_does_not_exist(self):
        self.client.post(self.login, self.auth, format='text/html')
        response = self.client.post(self.delete, self.invalid_data_delete, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Unable to delete this product."}')

    def test_cart_view_remove_prodct_when_product_user_not_auth(self):
        response = self.client.post(self.delete, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "You must be authenticated to delete this product"}')

    def test_cart_view_when_transaction_complete(self):
        self.client.post(self.login, self.auth, format='text/html')
        self.cart_user = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart_user.mark_as_complete()
        response = self.client.get(self.orders)
        self.assertEqual(response.status_code, 200)

    def test_cart_view_when_transaction_complete_and_user_not_auth(self):
        self.cart_user = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart_user.mark_as_complete()
        response = self.client.get(self.orders)
        self.assertEqual(response.status_code, 302)

    def test_order_details_view_with_no_coupon(self):
        self.client.post(self.login, self.auth, format='text/html')
        self.cart_user = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart_user.mark_as_complete()
        response = self.client.get(self.details)
        self.assertEqual(response.status_code, 200)

    def test_order_details_view_with_coupon(self):
        self.client.post(self.login, self.auth, format='text/html')
        self.cart2.add_coupon(self.coupon)
        self.cart2.mark_as_complete()
        self.assertEqual(self.cart2.coupon.coupon, 'coupon')
        self.assertEqual(self.cart2.coupon.discount, 15)
        response = self.client.get(self.details)
        self.assertEqual(response.status_code, 200)
