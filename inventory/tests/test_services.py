"""
Unit testing for the donation assistance application.
"""

from django.test import TestCase, RequestFactory
from unittest.mock import patch  # Using this for mock tests
from django.contrib.sessions.middleware import SessionMiddleware
from inventory.models import Item
from inventory.services import DonationCart

# Create your tests here.
class DonationCartTests(TestCase):
    def setUp(self):
        # Use a patch as a context manager or decorator. Allows for us to test without
        # hitting the API.
        with patch('inventory.models.amazon_api.get_product_info') as mock_api:
            mock_api.return_value = {
                'name': 'Test Item',
                'price': 10.00,
                'image': 'http://test.com'
            }
            self.item = Item.objects.create(
                name='Test Item',
                amazon_product_url='https://amazon.com',
                max_quantity=10,
                quantity = 0
            )

        self.factory = RequestFactory()
        self.request = self.factory.get('/')

        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(self.request)
        self.request.session.save()
        self.cart_service = DonationCart()

    
    def test_cart_caps_at_max_quantity(self):
        """ Test that checks that the cart won't exceed (max_quantity - current_quantity)"""
        # Item has max_quantity=10 and quantity=0
        message = self.cart_service.add_item_to_session_cart(
            self.request.session,
            self.item.pk,
            15
        )

        cart_qty = self.request.session['cart'][str(self.item.pk)]['quantity']
        # We should see it capped at 10
        self.assertEqual(cart_qty, 10)
        # We should see a user message that informs us that we have reached the item stock limit.
        self.assertIn(f'We only need 10 more', message)


    def test_view_rejects_long_input(self):
        """Test that the view redirects and logs error for len > 7"""
        from django.urls import reverse
        url = reverse('add_to_cart', args=[self.item.pk])

        # We will send a 15-digit number
        response = self.client.post(url, {'quantity': '123456789012345'})

        # It should redirect back to item_list
        self.assertEqual(response.status_code, 302)
        # Check that it didn't add 123456789012345 to the session.
        # (The session will likely be empty because of the redirect inside a unit test).
        cart = self.client.session.get('cart', {})
        self.assertEqual(cart.get(str(self.item.pk), {}).get('quantity'), None)



class ItemPriorityTests(TestCase):

    @patch('inventory.models.amazon_api.get_product_info')
    def test_priority_calculation(self, mock_api):
        """ Test that priority_level is correctly set based on quantity ratio."""
        # Mock the API so it doesn't run during save()
        mock_api.return_value = {'name': 'Test', 'price': 10.0, 'image': ''}

        dummy_url = "https://amazon.com"

        # Scenario 1: Urgent (10% stock)
        # 1/10 = 0.10 (< lvl_1= 20%) -> Should be priority 5.
        item_urgent = Item.objects.create(name='Urgent Item', quantity=1, max_quantity=10, amazon_product_url=dummy_url)
        self.assertEqual(item_urgent.priority_level, 5)

        # Scenario 2: Moderate (50% stock)
        # 5/10 = 0.50 (= lvl_3 50%) -> Should be priority 3.
        item_mid = Item.objects.create(name='Mid Item', quantity=5, max_quantity=10, amazon_product_url=dummy_url)
        self.assertEqual(item_mid.priority_level, 3)

        # Scenario 3: Low urgency (90% stock)
        # 19/20 = 0.95 (= lvl_5 95%) -> Should be priority 1.
        item_full = Item.objects.create(name='Full Item', quantity=19, max_quantity=20, amazon_product_url=dummy_url)
        self.assertEqual(item_full.priority_level, 1)
