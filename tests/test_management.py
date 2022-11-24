from django.test import TestCase
from django.urls import reverse

from account.models import Account, Cart, OrderStatus

from product.models import Product, ProductAttribute, Color, Size

from feedback.models import FeedbackModel


class BaseTest(TestCase):
    def setUp(self):
        # Create superuser
        self.user = Account.objects.create_superuser(name='ExampleName', surname='ExampleSurname', email='ExampleNEw@gmail.com', gender='Man', phone_number='32111222333', password='ExamplePassword123')
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
        # Create other user
        self.other_user = Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='Example@gmail.com', gender='Man', phone_number='32231222333', password='ExamplePassword123')
        self.other_user_auth = {'email': 'Example@gmail.com', 'password': 'ExamplePassword123'}
        # Product data
        self.valid_product_data = {
            'category': 'Jeans',
            'name': 'Jeans',
            'description': 'Description',
            'price': 100.00,
            'gender': 'Man',
            'composition': 'Jeans 100%',
            'sizes': 'L',
            'colors': 'Red',
         }
        self.invalid_product_data = {
            'category': 'T-shirts',
            'name': 'Base T-shirt',
            'description': 'Description',
            'price': 100.00,
            'gender': 'Man',
            'composition': 'Jeans 100%',
            'sizes': 'L',
            'colors': 'Red',
        }
        self.coupon_data = {
            'coupon': 'test',
            'discount': 15,
        }

        # Create product attributes
        self.attr = ProductAttribute.objects.create(category='T-shirts', name='Base T-shirt', description='Description', price=50.00, gender='Man', composition='Cotton 100%',)
        # Create color and size
        self.color = Color.objects.create(color='Red')
        self.size = Size.objects.create(size='L')
        # Create product
        self.product = Product.objects.create(product=self.attr)
        self.product.sizes .add(self.size)
        self.product.colors.add(self.color)
        self.product.save()
        # Add product to cart and mark as complete
        self.user_cart = Cart.objects.get(user=self.user)
        self.user_cart.add_product(product=self.product, quantity=1, color=self.color, size=self.size, user=self.user)
        self.user_cart.mark_as_complete()
        # Create feedback ,question. issue
        self.feedback = FeedbackModel.objects.create(user=self.user, subject='Feedback', message='Test')
        self.question = FeedbackModel.objects.create(user=self.user, subject='Question', message='Test')
        self.issue = FeedbackModel.objects.create(user=self.user, subject='Issue', message='Test')
        # New status data
        self.new_status = {
            'order_id': self.user_cart.id,
            'new_status': 'Waiting for shipment'
        }
        # URLS
        self.login_url = reverse('login')
        self.product_add_url = reverse('management:product_add')
        self.collecting_items = reverse('management:collecting')
        self.waiting_for_shipment = reverse('management:ready')
        self.shipped = reverse('management:shipped')
        self.delivered = reverse('management:delivered')
        self.add_coupon_url = reverse('management:add_coupon')
        self.coupon_management_url = reverse('management:coupons_management')
        self.feedback_url = reverse('management:feedback')
        self.questions_url = reverse('management:questions')
        self.issues_url = reverse('management:issues')
        self.order_details_url = reverse('management:details', kwargs={'order_id': self.user_cart.id, 'status': 1})
        self.set_new_Status_url = reverse('management:set_new_status')
        return super().setUp()


class ManagementTest(BaseTest):
    def test_add_product_get(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.product_add_url)
        self.assertEqual(response.status_code, 200)

    def test_add_product_post(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.product_add_url, self.valid_product_data)
        self.assertEqual(response.status_code, 302)

    def test_add_product_post_invalid(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.product_add_url, self.invalid_product_data)
        self.assertEqual(response.status_code, 200)

    def test_orders_with_status_collecting_an_items(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.collecting_items)
        self.assertEqual(response.status_code, 200)

    def test_orders_with_status_waiting_for_shipment(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        OrderStatus.objects.create(order=self.user_cart, status='Waiting for shipment')
        response = self.client.get(self.waiting_for_shipment)
        self.assertEqual(response.status_code, 200)

    def test_orders_with_status_shipped(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        OrderStatus.objects.create(order=self.user_cart, status='Waiting for shipment')
        OrderStatus.objects.create(order=self.user_cart, status='Shipped')
        response = self.client.get(self.shipped)
        self.assertEqual(response.status_code, 200)

    def test_orders_with_status_delivered(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        OrderStatus.objects.create(order=self.user_cart, status='Waiting for shipment')
        OrderStatus.objects.create(order=self.user_cart, status='Shipped')
        OrderStatus.objects.create(order=self.user_cart, status='Delivered')
        response = self.client.get(self.delivered)
        self.assertEqual(response.status_code, 200)

    def test_coupon_add_get(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.add_coupon_url)
        self.assertEqual(response.status_code, 200)

    def test_coupon_add_post(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.add_coupon_url, self.coupon_data)
        self.assertEqual(response.status_code, 302)

    def test_coupon_add_post_invalid(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.client.post(self.add_coupon_url, self.coupon_data)
        response = self.client.post(self.add_coupon_url, self.coupon_data)
        self.assertEqual(response.status_code, 200)

    def test_coupons_management(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.client.post(self.add_coupon_url, self.coupon_data)
        response = self.client.get(self.coupon_management_url)
        self.assertEqual(response.status_code, 200)

    def test_feedback(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.feedback_url)
        self.assertEqual(response.status_code, 200)

    def test_questions(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.questions_url)
        self.assertEqual(response.status_code, 200)

    def test_issues(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.issues_url)
        self.assertEqual(response.status_code, 200)

    def test_orders_details(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.order_details_url)
        self.assertEqual(response.status_code, 200)

    def test_set_new_status(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.set_new_Status_url, self.new_status, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "Success"}')

    def test_set_new_status_when_order_does_not_exist(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.new_data = {'order_id': 123, 'status': 'Waiting for shipment'}
        response = self.client.post(self.set_new_Status_url, self.new_data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "Unable to update status"}')

    def test_set_new_status_when_user_not_staff(self):
        self.client.post(self.login_url, self.other_user_auth, format='text/html')
        response = self.client.post(self.set_new_Status_url, self.new_status, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "You must be authenticated to change the status"}')
