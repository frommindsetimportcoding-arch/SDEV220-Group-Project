from .models import Item
from random import uniform
import time
from datetime import timedelta
import requests
import logging
from django.conf import settings
import serpapi
import re


class InventoryLogic:
    """
    Should order items by urgency level. Prioritization logic should be implemented here. Get best price. 
    """

    def get_all_items(self):
        return Item.objects.all()
    
    
    def get_prioritized_items(self):
        """
        Orders itmes by prioritization level. 5 being the highest and 1 being the lowest.
        Does so in descending order. Personal note: The '-' in '-priority_level' is what sorts in descending order.
        Filtering the object to remove anything from the donor list that would have a priority level 1 which is near full capacity. 
        """
        return Item.objects.filter(priority_level__gt=1).order_by('-priority_level')
    
    def get_items_with_prices(self, session): # get_items_with_price_and_image
        simulator = PriceSimulator()
        items = self.get_prioritized_items()

        result = []

        for item in items:
            vendor, price = simulator.get_price_with_cache(session, item)

            result.append({'id': item.id,
                           'name': item.name,
                           'quantity': item.quantity,  # will get rid of this before production. 
                           'description': item.description,
                           'priority': item.priority_level, # Will get rid of this before production. 
                           'cheapest_vendor': vendor,
                           'cheapest_price':price
                           })
        return result 
# New code testing to see if it works. 
    def add_item_to_session_cart(self, session, item_id, quantity):
        cart = session.get('cart', {})
        item = Item.objects.get(id=item_id)

        simulator = PriceSimulator()
        vendor, price = simulator.get_price_with_cache(session, item)

        str_id = str(item_id)

        if str_id in cart:
            cart[str_id]['quantity'] += int(quantity)
        else:
            cart[str_id] = {
                'quantity': int(quantity),
                'vendor': vendor,
                'price': price
            }

        session['cart'] = cart
        session.modified = True  # This line of code tells Django that the dictionary was changed.


class AmazonApi:
    """ serpApi will be used to parse product information into variables. """
    SERPAPI_KEY = settings.SERPAPI_KEY
    def __init__(self):
        self.client = serpapi.Client(api_key=self.SERPAPI_KEY)
    
    
    def extract_asin(url):
        """ Extract ASIN from Amazon URL."""
        match = re.search(r'/dp/[A-Z0-9]{10}', url)
        if match:
            return match.group(1)
        
        match = re.search(r'/product/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
        
        return None
    
    
    def get_product_info(self, asin):
        
        if not asin:
            return None
        
        results = self.client.search({
            "engine": "amazon_product",
            "asin": asin,
            "amazon_domain": "amazon.com"
        })
        return self._parse_results(results)


    def _parse_results(self, results):
        product = results.get('product_results', {})

        return {
            'name': product.get('title'),
            'price': product.get('extracted_price'),
            'image': self._get_main_image(product),
        }

    def _get_main_image(self, product):
        images = product.get('thumbnails', [])
        return images[0] if images else product.get('thumbnail') 

# Ignore below unless I find some of this useful for the API integration

# class PriceSimulator:
#     """
#     This will generate simulated prices for three 'Vendors' setting a lower range of the unit_price * 0.7 
#     and an upper range of the unit_price * 1.3. Returns a dictionary 'prices' with the vendor: price. 
#     """


#     VENDORS = ['Amazon', 'Walmart', 'Target']
#     PRICE_TTL = 10

#     def generate_vendor_prices(self, item):
#         prices = {}
        
#         for vendor in self.VENDORS:
#             price = uniform(item.unit_price * 0.7, item.unit_price * 1.3)
#             prices[vendor] = round(price, 2)

#         return prices 


#     def get_lowest_price(self, item):
#         prices = self.generate_vendor_prices(item)
#         vendor = min(prices, key=prices.get)
#         return vendor, prices[vendor]
    
#     def get_price_with_cache(self, session, item):
#         price_cache = session.get("prices", {})
#         item_key = str(item.id)

#         current_time = time.time()

#         if item_key in price_cache:
#             cached = price_cache[item_key]

#             if current_time - cached["timestamp"] < self.PRICE_TTL:
#                 return cached['vendor'], cached['price']
            
#         vendor, price = self.get_lowest_price(item)

#         price_cache[item_key] = {
#             'vendor': vendor,
#             'price': price,
#             'timestamp': current_time
#         }

#         session['prices'] = price_cache
#         session.modified = True

#         return vendor, price 

class DonationCart:
    pass