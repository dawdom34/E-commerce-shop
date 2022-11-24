from django.test import TestCase
from django.urls import reverse

from account.models import Account, Cart, CartItem
from product.models import Product, ProductAttribute, Size, Color
from coupons.models import Coupon
from coupons.forms import CouponForm


class BaseTest(TestCase):
    def setUp(self):
        # Create user
        self.user = Account.objects.create_superuser(name='ExampleName', surname='ExampleSurname', email='ExampleNEw@gmail.com', gender='Man', phone_number='32111222333', password='ExamplePassword123')
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
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
        # Create coupon
        self.coupon = Coupon.objects.create(coupon='test', discount=15) 
        # Add product to cart
        self.cart = Cart.objects.get(user=self.user)
        self.cart.add_product(self.product, 2, self.color, self.size, self.user)
        # URLS
        self.login_url = reverse('login')
        self.coupon_add_url = reverse('coupons:coupon_apply')
        self.change_coupon_status_url = reverse('coupons:coupon_change_status')
        # json data
        self.data = {'coupon': self.coupon, 'cart_id': self.cart.id}
        self.invalid_coupon = {'coupon': 'invalid', 'cart_id': self.cart.id}
        self.invalid_id = {'coupon': self.coupon, 'cart_id': 123}
        return super().setUp()


class CouponTest(BaseTest):
    def test_valid_coupon_apply(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.coupon_add_url, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Coupon applied."}')

    def test_invalid_coupon_cart_id(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.coupon_add_url, self.invalid_id, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Unable to apply this coupon."}')

    def test_invalid_coupon(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.coupon_add_url, self.invalid_coupon, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Coupon does not exist."}')

    def test_coupon_already_in_use(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.client.post(self.coupon_add_url, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        response = self.client.post(self.coupon_add_url, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "You already have a coupon in use."}')

    def test_coupon_been_used_in_the_past(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        # Add coupon to the cart
        self.cart.add_coupon(self.coupon)
        # Mark cart as complete
        self.cart.mark_as_complete()
        self.assertEqual(self.cart.coupon, self.coupon)
        # Get the new cart
        self.new_user_cart = Cart.objects.get(user=self.user, transaction_completed=False)
        self.assertFalse(self.new_user_cart.coupon)
        # New json data
        self.new_data = {'coupon': self.coupon, 'cart_id': self.new_user_cart.id} 
        # Apply same coupon to the new cart
        response = self.client.post(self.coupon_add_url, self.new_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        # Check the results
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "You already used this coupon."}')

    def test_coupon_change_status_deactivate_and_activate(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        # json data
        data_deactivate = {'coupon_id': self.coupon.id, 'status': 'Deactivate'}
        data_activate = {'coupon_id': self.coupon.id, 'status': 'Activate'}
        # Deactivate
        response = self.client.post(self.change_coupon_status_url, data_deactivate, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Coupon status changed."}')

        # Activate
        response = self.client.post(self.change_coupon_status_url, data_activate, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Coupon status changed."}')

    def test_coupon_change_status_invalid_coupon_id(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        # json data
        data = {'coupon_id': 123, 'status': 'Deactivate'}
        response = self.client.post(self.change_coupon_status_url, data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Coupon does not exist."}')

    def test_coupon_change_status_with_invalid_status(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        # json data
        data = {'coupon_id': self.coupon.id, 'status': 'invalid'}
        response = self.client.post(self.change_coupon_status_url, data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": "Unable to change the status."}')

    def test_coupon_form(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        data = {'coupon': 'randomcoupon', 'discount': 15}
        form = CouponForm(data=data)
        self.assertEqual(form.errors, {})

    def test_coupon_form_if_name_already_in_use(self):
        # Login user
        self.client.post(self.login_url, self.user_auth, format='text/html')
        data = {'coupon': 'test', 'discount': 15}
        form = CouponForm(data=data)
        self.assertEqual(form.errors, {'__all__': ['Coupon name already in use']})
