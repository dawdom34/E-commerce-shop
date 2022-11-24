from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from account.models import Account, Address

from iso3166 import countries


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text='Add a valid email address.')
    phone_number = forms.TextInput()

    class Meta:
        model = Account
        fields = ('email', 'name', 'surname', 'gender', 'phone_number', 'password1', 'password2')

    def clean_email(self):
        """
        Check if email is already in use
        """
        email = self.cleaned_data['email'].lower()
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError(f'Email {email} is already in use.')

    def clean_phone_number(self):
        """
        Check if phone number is already in use
        """
        number = self.cleaned_data['phone_number']
        try:
            user = Account.objects.get(phone_number=number)
        except Account.DoesNotExist:
            return number
        raise forms.ValidationError(f'Phone number {number} is already in use.')


class AccountAuthenticationForm(forms.ModelForm):
    email = forms.EmailField(max_length=255)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError('Incorrect email or password!')
            return self.cleaned_data


class AddressForm(forms.ModelForm):
    address1 = forms.CharField(max_length=1024)
    address2 = forms.CharField(max_length=1024, empty_value=True)
    zip_code = forms.CharField(max_length=20)
    city = forms.CharField(max_length=1024)
    country = forms.CharField(max_length=1024)

    class Meta:
        model = Address
        fields = ('address1', 'address2', 'zip_code', 'city', 'country')

    # Pass authenticated user from view
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AddressForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.is_valid():
            address1 = self.cleaned_data['address1']
            address2 = self.cleaned_data['address2']
            zip_code = self.cleaned_data['zip_code']
            city = self.cleaned_data['city']
            country = self.cleaned_data['country']

            # User can only have 4 addresses
            user = Account.objects.get(pk=self.user.id)
            ad = Address.objects.filter(user=user)
            if len(ad) == 4:
                raise forms.ValidationError('You can only have 4 addresses')

            # Check if country have valid name
            try:
                c = countries.get(country)
            except:
                raise forms.ValidationError("That country doesn't exist")

            # Check if address already exist
            try:
                address = Address.objects.get(address1=address1, address2=address2,zip_code=zip_code, city=city, country=country)
            except:
                address = None
            if address != None:
                raise forms.ValidationError('You already have this address')


class AccountEditForm(forms.ModelForm):
    name = forms.CharField(max_length=60)
    surname = forms.CharField(max_length=80)
    email = forms.EmailField(max_length=100)
    phone_number = forms.CharField(max_length=20)

    class Meta:
        model = Account
        fields = ('name', 'surname', 'email', 'phone_number')

    def clean_email(self):
        """
        Check if email already exist
        """
        email = self.cleaned_data['email'].lower()
        try:
            user = Account.objects.exclude(pk=self.instance.pk).get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError(f'Email {email} is already in use.')

    def clean_phone_number(self):
        """
        Check if phone number already exist
        """
        number = self.cleaned_data['phone_number']
        try:
            user = Account.objects.exclude(pk=self.instance.pk).get(phone_number=number)
        except Account.DoesNotExist:
            return number
        raise forms.ValidationError(f'Phone number {number} is already in use.')

    def save(self, commit=True):
        user = super(AccountEditForm, self).save(commit=False)
        user.name = self.cleaned_data['name']
        user.surname = self.cleaned_data['surname']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
        return user
