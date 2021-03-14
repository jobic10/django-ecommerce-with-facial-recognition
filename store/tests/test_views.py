from django.test import TestCase
from django.urls import reverse
from store import models
from django.contrib.auth.models import User


class TestViews(TestCase):
    """
    Testing our views: response codes, templates, redirects.
    """
    def setUp(self):
        self.store_url = reverse('store')
        self.cart_url = reverse('cart')
        self.checkout_url = reverse('checkout')
        self.update_url = reverse('update')
        self.validate_form_url = reverse('validate_form')
        self.order_url = reverse('order')
        self.orders_url = reverse('orders')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.registration_url = reverse('registration')

        self.username = 'root'
        self.password = 'azaza2222'
        self.email = 'root@root.com'
        self.product_name = 'test_product'
        self.price = 1000

    def make_registration(self):
        registration = self.client.post(self.registration_url, {'username': self.username,
                                                 'email': self.email,
                                                 'password1': self.password,
                                                 'password2': self.password})
        return registration

    def make_login(self):
        log = self.client.post(self.login_url, {'username': self.username, 'password': self.password})
        return log

    def make_product(self):
        product = models.Product.objects.create(name=self.product_name, price=self.price, digital=False)
        return product

    def test_class_methods(self):
        self.make_registration()
        user = User.objects.all().first()
        self.assertEqual(user.username, self.username)

        self.make_product()
        product = models.Product.objects.all().first()
        self.assertEqual(product.name, self.product_name)

    def test_store_view_GET(self):
        response = self.client.get(self.store_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/store.html')

    def test_store_cart_GET(self):
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/cart.html')

    def test_store_checkout_GET(self):
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/checkout.html')

    def test_store_update_cart_POST(self):
        # invalid id and action
        response = self.client.post(self.update_url, {'data1': 'data1', 'data2': 'data2'})
        self.assertEqual(response.status_code, 400)

        product = self.make_product()

        # invalid id
        response = self.client.post(self.update_url, {'id': '10', 'action': 'add'})
        self.assertEqual(response.status_code, 422)

        # invalid action
        response = self.client.post(self.update_url, {'id': '1', 'action': 'lol'})
        self.assertEqual(response.status_code, 422)

        # valid id and action count +
        response = self.client.post(self.update_url, {'id': '1', 'action': 'add'})
        self.assertEqual(response.status_code, 200)
        order_item_count = models.OrderItem.objects.all().count()
        self.assertEqual(order_item_count, 1)

        # valid id and action count -
        response = self.client.post(self.update_url, {'id': '1', 'action': 'remove'})
        self.assertEqual(response.status_code, 200)
        order_item_count = models.OrderItem.objects.all().count()
        self.assertEqual(order_item_count, 0)

    def test_store_update_cart_GET(self):
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 405)

    def test_store_validate_form_POST(self):
        # test if user submit occupied email
        self.make_registration()
        response = self.client.post(self.validate_form_url, {'name': 'test_name', 'email': self.email})
        self.assertEqual(response.status_code, 400)

        # make product and add it to users cart
        product = self.make_product()
        self.client.post(self.update_url, {'id': product.id, 'action': 'add'})

        # incomplete shipping address: without phone
        response = self.client.post(self.validate_form_url, {'id': product.id, 'action': 'add',
                                                             'address': 'test address', 'city': 'test city'})
        self.assertEqual(response.status_code, 400)

        # incomplete shipping address: without address
        response = self.client.post(self.validate_form_url, {'id': product.id, 'action': 'add',
                                                             'phone': 'test phone', 'city': 'test city'})
        self.assertEqual(response.status_code, 400)

        # correct shipping address
        response = self.client.post(self.validate_form_url, {'id': product.id, 'action': 'add',
                                                             'address': 'test address', 'city': 'test city',
                                                             'phone': 'test phone'})
        self.assertEqual(response.status_code, 200)

    def test_store_validate_form_GET(self):
        response = self.client.get(self.validate_form_url)
        self.assertEqual(response.status_code, 405)

    def test_store_completed_order_GET(self):
        response = self.client.get(self.order_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/order.html')

    def test_store_completed_orders_POST(self):
        # вернуться сюда когда настрою stripe и протестировать сразу нормально без костылей
        pass

    def test_store_registration_view_GET(self):
        # if unauthenticated
        response = self.client.get(self.registration_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/registration.html')

        # if authenticated
        self.make_registration()
        self.make_login()
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)

    def test_store_registration_view_POST(self):
        # submit valid data
        response = self.make_registration()
        self.assertEqual(response.status_code, 302)

        # submit invalid data: without username
        response = self.client.post(self.registration_url, {'email': 'elf0@list.ruy',
                                                            'password1': 'azaza2222', 'password2': 'azaza2222'})
        self.assertEqual(response.status_code, 400)

        # submit invalid data: password1 != password 2
        response = self.client.post(self.registration_url, {'username': 'artem2', 'email': 'elf0@list.ruy',
                                                            'password1': 'azaza2222', 'password2': 'ololo2222'})
        self.assertEqual(response.status_code, 400)

    def test_store_login_view_GET(self):
        # if unauthenticated
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/login.html')

        # if authenticated
        self.make_registration()
        self.make_login()
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)

    def test_store_login_view_POST(self):
        # create user
        self.make_registration()

        # if invalid login/password
        response = self.client.post(self.login_url, {'username': 'incorrect_login', 'password': 'incorrect_password'})
        self.assertEqual(response.status_code, 200)

        # if valid login/password
        response = self.make_login()
        self.assertEqual(response.status_code, 302)

    def test_store_logout_view(self):
        self.make_registration()
        self.make_login()
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)










