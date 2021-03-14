from django.test import SimpleTestCase
from django.urls import reverse, resolve
from store import views


class TestUrls(SimpleTestCase):
    """
    Testing url resolving.
    """
    def test_if_urls_resolved(self):
        """
        Testing if every url resolves as we expect. Honestly don`t know if there is any sense testing it...
        """
        url = reverse('store')
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func, views.store)

        url = reverse('checkout')
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func, views.checkout)

        url = reverse('update')
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func, views.update_cart)

        url = reverse('validate_form')
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func, views.validate_form)

        url = reverse('order')
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func, views.completed_order)

        url = reverse('orders')
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func, views.completed_orders)

        url = reverse('login')
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func, views.login_view)

        url = reverse('logout')
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func, views.logout_view)

        url = reverse('registration')
        resolved_url = resolve(url)
        self.assertEqual(resolved_url.func, views.registration_view)

















