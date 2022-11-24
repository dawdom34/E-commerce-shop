from django.test import TestCase
from django.urls import reverse

from account.models import Account, Cart

from product.models import Product, ProductAttribute, Size, Color

from feedback.models import FeedbackModel


class BaseTest(TestCase):
    def setUp(self):
        # Create user
        self.user = Account.objects.create_superuser(email='Basicemail@gmail.com', name='Name', surname='Surname', gender='Man', phone_number=11123123123, password='Simplepassword123')
        self.user_auth = {'email': 'Basicemail@gmail.com', 'password': 'Simplepassword123'}
        # Create other user
        self.other_user = Account.objects.create_user(email='Basicnewemail@gmail.com', name='Name', surname='Surname', gender='Man', phone_number=11153123123, password='Simplepassword123')
        self.other_user_auth = {'email': 'Basicnewemail@gmail.com', 'password': 'Simplepassword123'}
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
        self.cart1 = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart1.add_product(self.product, 4, self.color, self.size, self.user)
        # URLS
        self.login_url = reverse('login')
        self.add_feedback_url = reverse('feedback:send')
        self.mark_as_complete = reverse('feedback:mark_as_complete')
        return super().setUp()


class FeedbackTest(BaseTest):
    def test_add_feedback_get(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.add_feedback_url)
        self.assertEqual(response.status_code, 200)

    def test_add_feedback_post(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        data = {'subject': 'Feedback', 'message': 'Test'}
        response = self.client.post(self.add_feedback_url, data)
        self.assertEqual(response.status_code, 302)

    def test_add_feedback_post_invalid(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        data = {'subject': '', 'message': 'Test'}
        response = self.client.post(self.add_feedback_url, data)
        self.assertEqual(response.status_code, 200)

    def test_feedback_mark_as_complete(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        data = {'subject': 'Feedback', 'message': 'Test'}
        self.client.post(self.add_feedback_url, data)
        message = FeedbackModel.objects.get(user=self.user)
        data2 = {'message_id': message.id}
        response = self.client.post(self.mark_as_complete, data2, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "Success."}')

    def test_feedback_mark_as_complete_with_invalid_id(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        data = {'subject': 'Feedback', 'message': 'Test'}
        self.client.post(self.add_feedback_url, data)
        data2 = {'message_id': 123}
        response = self.client.post(self.mark_as_complete, data2, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "Feedback message does not exist."}')

    def test_feedback_mark_as_complete_when_user_not_staff(self):
        self.client.post(self.login_url, self.other_user_auth, format='text/html')
        data = {'subject': 'Feedback', 'message': 'Test'}
        self.client.post(self.add_feedback_url, data)
        message = FeedbackModel.objects.get(user=self.other_user)
        data2 = {'message_id': message.id}
        response = self.client.post(self.mark_as_complete, data2, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "Access denied"}')

    def test_feedback_details(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        data = {'subject': 'Feedback', 'message': 'Test'}
        self.client.post(self.add_feedback_url, data)
        message = FeedbackModel.objects.get(user=self.user)
        self.details = reverse('feedback:details', kwargs={'message_id': message.id})
        response = self.client.get(self.details)
        self.assertEqual(response.status_code, 200)

    def test_feedback_details_with_invalid_id(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.details = reverse('feedback:details', kwargs={'message_id': 123})
        response = self.client.get(self.details)
        self.assertEqual(response.content, b'Feedback object does not exist.')
