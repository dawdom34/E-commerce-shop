from django.test import TestCase
from django.urls import reverse

from account.models import Account, Cart, Address
from product.models import Product, ProductAttribute, ProductAttribute, Color, Size, Review
from product.forms import FilterForm, ProductCreationForm


class BaseTest(TestCase):
    def setUp(self):
        # Create user
        self.user = Account.objects.create_superuser(name='ExampleName', surname='ExampleSurname', email='ExampleNEw@gmail.com', gender='Man', phone_number='32111222333', password='ExamplePassword123')
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
        # Create other user
        self.other_user = Account.objects.create_superuser(name='ExampleName', surname='ExampleSurname', email='Example@gmail.com', gender='Man', phone_number='32231222333', password='ExamplePassword123')
        self.other_user_auth = {'email': 'Example@gmail.com', 'password': 'ExamplePassword123'}
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
        # Create address
        self.address1 = Address.objects.create(address1='address1', address2='address2', zip_code='12-345', city='Berlin', country='Germany', user=self.user)
        # Add product to cart
        self.cart1 = Cart.objects.get(user=self.user, transaction_completed=False)
        self.cart1.add_product(self.product, 4, self.color, self.size, self.user)
        self.cart2 = Cart.objects.get(user=self.other_user, transaction_completed=False)
        self.cart2.add_product(self.product, 4, self.color, self.size, self.other_user)
        # Add address to cart
        self.cart1.add_address(self.address1.id)
        self.cart1.mark_as_complete()
        # Create reviev of a product
        self.rev = Review.objects.create(user=self.user, product=self.product, score=4, review='ok')

        # URLS
        self.login_url = reverse('login')
        self.home_url = reverse('shop:home')
        self.filtered_products = reverse('shop:filtered', kwargs={'category': 'T-shirts'})
        self.product_details = reverse('shop:details', kwargs={'product_id': self.product.id})
        self.review_add = reverse('shop:add_product_review')
        self.review_delete = reverse('shop:delete_product_review')
        return super().setUp()


class ProductTest(BaseTest):
    def test_home_view(self):
        self.client.post(self.login_url, self.other_user_auth, format='text/html')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('shop_app/home.html')

    def test_filtered_products_view(self):
        self.client.post(self.login_url, self.other_user_auth, format='text/html')
        response = self.client.get(self.filtered_products)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('product/filtered.html')

    def test_filtered_products_view_when_user_not_auth(self):
        response = self.client.get(self.filtered_products)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('product/filtered.html')

    def test_filtered_products_post(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        data1 = {'category': 'T-shirts', 'size': 'L', 'gender': 'man', 'price': '100 to 150'}
        data2 = {'category': 'T-shirts', 'size': 'L', 'gender': 'man', 'price': '50 or less'}
        data3 = {'category': 'T-shirts', 'size': 'L', 'gender': 'man', 'price': '50 to 100'}
        data4 = {'category': 'T-shirts', 'size': 'L', 'gender': 'man', 'price': '150+'}
        data5 = {'category': '', 'size': 'L', 'gender': 'man', 'price': '150+'}
        response1 = self.client.post(self.filtered_products, data1, format='text/html')
        response2 = self.client.post(self.filtered_products, data2, format='text/html')
        response3 = self.client.post(self.filtered_products, data3, format='text/html')
        response4 = self.client.post(self.filtered_products, data4, format='text/html')
        response5 = self.client.post(self.filtered_products, data5, format='text/html')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response4.status_code, 200)
        self.assertEqual(response5.status_code, 401)

    def test_filtered_post_when_user_not_auth(self):
        data1 = {'category': 'T-shirts', 'size': 'L', 'gender': 'man', 'price': '100 to 150'}
        response1 = self.client.post(self.filtered_products, data1, format='text/html')
        self.assertEqual(response1.status_code, 200)

    def test_product_details(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.product_details)
        self.assertEqual(response.status_code, 200)

    def test_product_details_when_user_not_auth(self):
        response = self.client.get(self.product_details)
        self.assertEqual(response.status_code, 200)

    def test_product_details_when_user_without_review(self):
        self.client.post(self.login_url, self.other_user_auth, format='text/html')
        response = self.client.get(self.product_details)
        self.assertEqual(response.status_code, 200)

    def test_filtered_products_form_valid(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        data = {'category': 'T-shirts', 'size': 'L', 'gender': 'man', 'price': '100 to 150'}
        form = FilterForm(data=data)
        self.assertEqual(form.errors, {})

    def test_add_product_review(self):
        self.client.post(self.login_url, self.other_user_auth, format='text/html')
        self.data = {'review': 'ok', 'stars': 4, 'product_id': self.product.id}
        response = self.client.post(self.review_add, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "Review added."}')

    def test_add_product_review_with_invalid_product_id(self):
        self.client.post(self.login_url, self.other_user_auth, format='text/html')
        self.data = {'review': 'ok', 'stars': 4, 'product_id': 123}
        response = self.client.post(self.review_add, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "Unable to add this review."}')

    def test_add_product_review_when_user_not_auth(self):
        self.data = {'review': 'ok', 'stars': 4, 'product_id': 123}
        response = self.client.post(self.review_add, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "You must be authenticated to add review."}')

    def test_add_product_review_when_user_already_rated(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.data = {'review': 'ok', 'stars': 4, 'product_id': self.product.id}
        response = self.client.post(self.review_add, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "You have already rated this product."}')

    def test_delete_product_review(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.data = {'review_id': self.rev.id}
        response = self.client.post(self.review_delete, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "Review deleted."}')

    def test_delete_product_review_with_invalid_product_id(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.data = {'review_id': 123}
        response = self.client.post(self.review_delete, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "Unable to delete this review."}')

    def test_delete_product_review_when_user_not_auth(self):
        self.data = {'review_id': self.rev.id}
        response = self.client.post(self.review_delete, self.data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.content, b'{"response": "You must be authenticated to delete this review."}')

    def test_add_product_form(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.prod_data = {
            'category': 'Jeans',
            'name': 'Jeans',
            'description': 'Test',
            'price': 100.00,
            'gender': 'Man',
            'composition': 'Jeans 100%',
            'sizes': ['L'],
            'colors': ['Blue']
        }
        form = ProductCreationForm(self.prod_data)
        self.assertEqual(form.errors, {})

    def test_add_product_form_invalid_name(self):
        self.client.post(self.login_url, self.user_auth, format='text/html')
        self.prod_data = {
            'category': 'Jeans',
            'name': 'Product name',
            'description': 'Test',
            'price': 100.00,
            'gender': 'Man',
            'composition': 'Jeans 100%',
            'sizes': ['L'],
            'colors': ['Blue']
        }
        form = ProductCreationForm(self.prod_data)
        self.assertEqual(form.errors, {'name': ['Product name Product name is already in use.']})
