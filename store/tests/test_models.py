from django.test import TestCase
from django.urls import reverse
from store import models
from django.contrib.auth.models import User


class TestModels(TestCase):
    """
    Testing our models: property methods.
    """
    def setUp(self):
        self.store_url = reverse('store')
        self.update_url = reverse('update')
        self.registration_url = reverse('registration')

        self.username = 'root'
        self.password = 'azaza2222'
        self.email = 'root@root.com'

    def make_registration(self):
        registration = self.client.post(self.registration_url, {'username': self.username,
                                                                 'email': self.email,
                                                                 'password1': self.password,
                                                                 'password2': self.password})
        return registration

    def make_login(self):
        log = self.client.post(self.login_url, {'username': self.username, 'password': self.password})
        return log

    def make_product(self, name, price, digital):
        product = models.Product.objects.create(name=name, price=price, digital=digital)
        return product

    def add_or_remove_item_to_cart(self, item_id, action):
        if action == 'add' or action == 'remove':
            add = self.client.post(self.update_url, {'id': item_id, 'action': action})
            return add
        return None

    def test_order_model(self):
        self.make_registration()
        product1 = self.make_product('test_name1', 1000, False)
        product2 = self.make_product('test_name2', 2000, True)

        # after registration there is no order
        orders = models.Order.objects.all().count()
        self.assertEqual(orders, 0)

        # making order for user just visiting store page
        self.client.get(self.store_url)
        orders = models.Order.objects.all().count()
        self.assertEqual(orders, 1)

        # checking default values
        order = models.Order.objects.all().first()
        self.assertEqual(order.shipping, False)
        self.assertEqual(order.get_cart_total, 0)
        self.assertEqual(order.get_item_total, 0)

        # adding product2 to the order
        self.add_or_remove_item_to_cart(product2.id, 'add')
        self.assertEqual(order.shipping, False)
        self.assertEqual(order.get_cart_total, 2000)
        self.assertEqual(order.get_item_total, 1)

        # adding product1 to the order
        self.add_or_remove_item_to_cart(product1.id, 'add')
        self.assertEqual(order.shipping, True)
        self.assertEqual(order.get_cart_total, 3000)
        self.assertEqual(order.get_item_total, 2)

        # remove product2 from the order
        self.add_or_remove_item_to_cart(product2.id, 'remove')
        self.assertEqual(order.shipping, True)
        self.assertEqual(order.get_cart_total, 1000)
        self.assertEqual(order.get_item_total, 1)

    def test_order_item_model(self):
        self.make_registration()
        product1 = self.make_product('test_name1', 1000, False)

        # making order for user just visiting store page
        self.client.get(self.store_url)

        # adding product1
        self.add_or_remove_item_to_cart(product1.id, 'add')
        order_items = models.OrderItem.objects.all()
        self.assertEqual(order_items.first().get_total, 1000)

        # adding product1 second time twice
        self.add_or_remove_item_to_cart(product1.id, 'add')
        self.add_or_remove_item_to_cart(product1.id, 'add')
        order_items = models.OrderItem.objects.all()
        self.assertEqual(order_items.first().get_total, 3000)

        # removing product1 once
        self.add_or_remove_item_to_cart(product1.id, 'remove')
        order_items = models.OrderItem.objects.all()
        self.assertEqual(order_items.first().get_total, 2000)

    def test_customer_model(self):
        # check if customer creates to user
        self.make_registration()
        user = User.objects.all().first()
        customer = models.Customer.objects.all().first()
        self.assertEqual(user.customer.name, customer.name)





