from django.test import TestCase
from django.urls import reverse
from account.models import Account, Cart
from account.forms import RegistrationForm


class BaseTest(TestCase):
    def setUp(self):
        # URLS
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        # Users
        self.user = Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='examplenew@gmail.com', gender='Man', phone_number='32111222333', password='ExamplePassword123')
        self.other_user = Account.objects.create_user(name='ExampleOtherName', surname='ExampleOtherSurname', email='ExampleOther@gmail.com', gender='Man', phone_number='32113222333', password='ExamplePassword123')
        return super().setUp()


class RegisterTest(BaseTest):
    def test_register_url(self):
        """
        Test if user can load the page
        """
        response = self.client.get(self.register_url)
        # Check for status code 200 (success status response)
        self.assertEqual(response.status_code, 200)
        # Check if url returned correct template
        self.assertTemplateUsed(response, 'account/register.html')

    def test_user_registration(self):
        """
        Testing user registration
        """
        # Initiate user creation
        user = Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='Example@gmail.com', gender='Man', phone_number='12123123123', password='ExamplePassword123')
        # Check if created user is instance of an Account model
        self.assertIsInstance(user, Account)
        # Check if the user attributes have been correctly assigned
        self.assertEqual(user.name, 'ExampleName')
        self.assertEqual(user.surname, 'ExampleSurname')
        self.assertEqual(user.email, 'Example@gmail.com')
        self.assertEqual(user.gender, 'Man')
        self.assertEqual(user.phone_number, '12123123123')
        # Check if user permissions have been correctly assigned
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_superuser)
        # Check string method
        self.assertEqual(str(user), 'ExampleName ExampleSurname')
        # Check has_perm method
        self.assertFalse(user.has_perm('example'))
        # Check has_module_perms method
        self.assertTrue(user.has_module_perms('example'))

    def test_cart_creation_after_user_register(self):
        """
        Test if after user registration new cart is created
        """
        # Initiate user creation
        user = Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='Example@gmail.com', gender='Man', phone_number='12123123123', password='ExamplePassword123')
        # Check if cart is instance of Cart model
        cart = Cart.objects.get(user=user, transaction_completed=False)
        self.assertIsInstance(cart, Cart)

    def test_super_user_registration(self):
        """
        Testing super user registration
        """
        # Initiate user creation
        user = Account.objects.create_superuser(name='ExampleName', surname='ExampleSurname', email='Example@gmail.com', gender='Man', phone_number='12123123123', password='ExamplePassword123')
        # Check if created user is instance of an Account model
        self.assertIsInstance(user, Account)
        # Check if the user attributes have been correctly assigned
        self.assertEqual(user.name, 'ExampleName')
        self.assertEqual(user.surname, 'ExampleSurname')
        self.assertEqual(user.email, 'Example@gmail.com')
        self.assertEqual(user.gender, 'Man')
        self.assertEqual(user.phone_number, '12123123123')
        # Check if user permissions have been correctly assigned
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_superuser)
        # Check string method
        self.assertEqual(str(user), 'ExampleName ExampleSurname')
        # Check has_perm method
        self.assertTrue(user.has_perm('example'))
        # Check has_module_perms method
        self.assertTrue(user.has_module_perms('example'))

    def test_user_register_error_with_no_valid_attributes(self):
        """
        Testing user registration errors with invalid attributes
        """
        # Without name, surname, email, gender, phone number
        self.assertRaises(ValueError, Account.objects.create_user, name='', surname='ExampleSurname', email='Example@gmail.com', gender='Man', phone_number='12123123123', password='ExamplePassword123')
        self.assertRaises(ValueError, Account.objects.create_user, name='ExampleName', surname='', email='Example@gmail.com', gender='Man', phone_number='12123123123', password='ExamplePassword123')
        self.assertRaises(ValueError, Account.objects.create_user, name='ExampleName', surname='ExampleSurname', email='', gender='Man', phone_number='12123123123', password='ExamplePassword123')
        self.assertRaises(ValueError, Account.objects.create_user, name='ExampleName', surname='ExampleSurname', email='Example@gmail.com', gender='', phone_number='12123123123', password='ExamplePassword123')
        self.assertRaises(ValueError, Account.objects.create_user, name='ExampleName', surname='ExampleSurname', email='Example@gmail.com', gender='Man', phone_number='', password='ExamplePassword123')
        # Testing invalid gender
        self.assertRaises(ValueError, Account.objects.create_user, name='ExampleName', surname='ExampleSurname', email='Example@gmail.com', gender='Undefined', phone_number='', password='ExamplePassword123')

    def test_user_register_error_message_with_no_valid_attributes(self):
        """
        Testing user registration error messages with invalid attribues
        """
        with self.assertRaisesMessage(ValueError, 'Users must have an email address.'):
            Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='', gender='Man', phone_number='12123123123', password='ExamplePassword123')
        with self.assertRaisesMessage(ValueError, 'Users must have a name.'):
            Account.objects.create_user(name='', surname='ExampleSurname', email='Example@gmail.com', gender='Man', phone_number='12123123123', password='ExamplePassword123')
        with self.assertRaisesMessage(ValueError, 'Users must have surname.'):
            Account.objects.create_user(name='ExampleName', surname='', email='Example@gmail.com', gender='Man', phone_number='12123123123', password='ExamplePassword123')
        with self.assertRaisesMessage(ValueError, 'Users must have a gender'):
            Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='Example@gmail.com', gender='', phone_number='12123123123', password='ExamplePassword123')
        with self.assertRaisesMessage(ValueError, 'Users must have a phone number.'):
            Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='Example@gmail.com', gender='Man', phone_number='', password='ExamplePassword123')
        with self.assertRaisesMessage(ValueError, 'Invalid gender.'):
            Account.objects.create_user(name='ExampleName', surname='ExampleSurname', email='Example@gmail.com', gender='Undefined', phone_number='12123123123', password='ExamplePassword123')

    def test_user_register_view(self):
        self.user_register = {'name': 'NameUser', 'surname': 'SurnameUser', 'email': 'NewEmail@gmail.com', 'gender': 'Man', 'phone_number': '43233323323', 'password1': 'ExamplePassword123', 'password2': 'ExamplePassword123'}
        response = self.client.post(self.register_url, self.user_register, format='text/html')
        self.assertEqual(response.status_code, 302)

    def test_user_register_view_with_invalid_attributes(self):
        self.user_register = {'name': 'NameUser', 'surname': '', 'email': 'NewEmail@gmail.com', 'gender': 'Man', 'phone_number': '43233323323', 'password1': 'ExamplePassword123', 'password2': 'ExamplePassword123'}
        response = self.client.post(self.register_url, self.user_register, format='text/html')
        self.assertEqual(response.status_code, 401)

    def test_user_register_with_phone_number_already_in_use(self):
        self.user_register = {
            'name': 'NameUser',
            'surname': 'SurnameUser',
            'email': 'Example@gmail.com',
            'gender': 'Man',
            'phone_number': '32111222333',
            'password1': 'ExamplePassword123',
            'password2': 'ExamplePassword123'}
        response = self.client.post(self.register_url, self.user_register)
        self.assertEqual(response.status_code, 401)
        form = RegistrationForm(data=self.user_register)
        self.assertEqual(form.errors, {'phone_number': ['Phone number 32111222333 is already in use.']})

    def test_user_register_with_email_already_in_use(self):
        self.user_register = {
            'name': 'NameUser',
            'surname': 'SurnameUser',
            'email': 'examplenew@gmail.com',
            'gender': 'Man',
            'phone_number': '43233323323',
            'password1': 'ExamplePassword123',
            'password2': 'ExamplePassword123'}
        response = self.client.post(self.register_url, self.user_register)
        self.assertEqual(response.status_code, 401)
        form = RegistrationForm(data=self.user_register)
        self.assertEqual(form.errors, {'email': ['Email examplenew@gmail.com is already in use.']})

    def test_user_register_view_when_user_is_already_authenticated(self):
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.register_url)
        self.assertEqual(response.content, b'You are already authenticated as ExampleName ExampleSurname.')


class LoginTest(BaseTest):
    def test_login_url(self):
        response = self.client.get(self.login_url)
        # Check for status code
        self.assertEqual(response.status_code, 200)
        # Check template
        self.assertTemplateUsed(response, 'account/login.html')

    def test_login_user_view(self):
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
        response = self.client.post(self.login_url, self.user_auth, format='text/html')
        # Check for status code 302 (redirect)
        self.assertEqual(response.status_code, 302)
    
    def test_login_view_with_next(self):
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
        self.next_login_url = '/login/?next=/account/1/'
        response = self.client.post(self.next_login_url, self.user_auth, format='text/html')
        self.assertEqual(response.status_code, 302)

    def test_login_view_if_user_already_authenticated(self):
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)

    def test_login_user_view_with_invalid_attributes(self):
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'WrongPassword'}
        response = self.client.post(self.login_url, self.user_auth, format='text/html')
        self.assertEqual(response.status_code, 401)
        
    def test_logout_view(self):
        self.logout_url = reverse('logout')
        self.user_auth = {'email': 'ExampleNEw@gmail.com', 'password': 'ExamplePassword123'}
        self.client.post(self.login_url, self.user_auth, format='text/html')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)
