from django.test import TestCase
from django.urls import reverse
from store import models
from store import forms


class TestForms(TestCase):
    """
    Testing forms, if everything is valid, invalid cases, amount of errors.
    """
    def setUp(self):
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

    def test_shipping_form(self):
        # if there is phone missing
        form = forms.ShippingForm(data={'address': 'test address', 'city': 'test city'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)

        # if there is address missing
        form = forms.ShippingForm(data={'phone': 'test phone', 'city': 'test city'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)

        # if everything is missing
        form = forms.ShippingForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)

        # if everything is ok
        form = forms.ShippingForm(data={'address': 'test address', 'city': 'test city', 'phone': 'phone'})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_create_user_form(self):
        # if there is username is missing
        form = forms.CreateUserForm(data={'password1': 'azaza2222', 'password2': 'azaza2222', 'email': 'email@email.com'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)

        # if there is email is missing
        form = forms.CreateUserForm(data={'password1': 'azaza2222', 'password2': 'azaza2222', 'username': 'ololo'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)

        # if there is password1 =! password2
        form = forms.CreateUserForm(data={'password1': 'azaza2222', 'password2': 'azaza3333', 'username': 'ololo',
                                          'email': 'ololo@ololo.com'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)

        # if there is data missing
        form = forms.CreateUserForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)

        # if everything is ok
        form = forms.CreateUserForm(data={'password1': 'azaza2222', 'password2': 'azaza2222', 'username': 'ololo',
                                          'email': 'ololo@ololo.com'})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

        # check email validation
        self.make_registration()
        form = forms.CreateUserForm(data={'password1': 'azaza2222', 'password2': 'azaza2222', 'username': 'ololo',
                                          'email': self.email})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)










