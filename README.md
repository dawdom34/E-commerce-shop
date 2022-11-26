# E-commerce-shop
E-commerce app made in django

## Features:
- ### User profile management
  User is able to edit his profile and change/reset his password
- ### Address management
  User can have up to four addresses in their account
- ### Cart
  The ability to add a product and discount coupon to user cart. The product includes quantity and color
- ### Products management
  If the user has the appropriate permissions, he can add new products
- ### Product reviews
  The user has the option of adding an opinion about the product, the opinion includes a comment and a rating on a scale of 1 to 5
- ### Discount coupon
  Staff is able to add new discount coupons
- ### Feedback
  Users can contact via the contact form
- ### Payment
  The payment option is simulated using stripe
  
## Screenshots of the application

![home_page](https://user-images.githubusercontent.com/79845962/204012073-d949121d-7ba6-4bb7-8da6-194d7976f61d.jpg)
![filtered](https://user-images.githubusercontent.com/79845962/204012106-dfdac37b-989d-46a4-8e30-9713e8b7b6c3.jpg)
![Details](https://user-images.githubusercontent.com/79845962/204012126-75a78bb6-cf49-4c5d-bae4-f64b53c52d8a.jpg)
![Cart](https://user-images.githubusercontent.com/79845962/204012131-d94c0825-9a09-4564-8b59-8bce6c00fbfc.jpg)
![Order](https://user-images.githubusercontent.com/79845962/204012146-4990a06e-b507-4ff9-ac2f-fdb9102c9e6d.jpg)
![db](https://user-images.githubusercontent.com/79845962/204083927-a06bbe10-0700-4459-86a1-8e9b184b461b.png)

## Setup(Windows)
1. Create virtual environment and activate it. To do this open cmd and execute commands below
```bash
python -m venv name
```
- change the name to whatever you prefer
- Change library to created folder and activate your environment
```bash
Scripts\activate
```
2. Open git bash and clone this repository
```bash
git clone https://github.com/dawdom34/E-commerce-shop.git
```
3. Change directory to E-commerce-shop
4. Now is the time to install all required packages to run this app
```bash
pip install -r requirements.txt
```
5. Create migrations files
```bash
python manage.py makemigrations
```
6. Apply all migrations
```bash
python manage.py migrate
```
7. Create superuser
```bash
python manage.py createsuperuser
```
- After execute this command follow the instructions
8. For now your database is empty. Let's change that by adding some products to work with
- Make sure you're in E-commerce-shop directory
- Run the command:
```bash
python manage.py runscript load_products
```
- This command will generate database objects based on data from csv file
9. Run the development server
```bash
python manage.py runserver
```
- Once the server is hosted, head over to http://127.0.0.1:8000/

## Stripe setup
Stripe is a suite of APIs powering online payment processing. It is required for the correct operation of the application.
Go to official stripe page and register your account - https://dashboard.stripe.com/register
When you register, go to the developers tab (upper right corner) and look for API keys (left sidebar).
In standard keys tab you will find two types of keys, publishable key and secret key, copy then to E-commerce-shop/shop-app/settings.py

![stripe](https://user-images.githubusercontent.com/79845962/204022434-0d20ed1b-53bb-46f6-8980-fa504f71c972.PNG)

## Now you're ready to have fun with this app

