"""
This file handles the business logic as it relates to the needs of Non-Profit organizations.
"""
import logging
from django.conf import settings
import serpapi
import re
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

class InventoryLogic:
    """
    Should order items by urgency level. Prioritization logic should be implemented here. Get best price. 
    """

    def get_all_items(self):
        from .models import Item
        return Item.objects.all() # Don't technically need this since we are getting items by filter. 
    
    
    def get_prioritized_items(self):
        """
        Orders itmes by prioritization level. 5 being the highest and 1 being the lowest.
        Does so in descending order. Personal note: The '-' in '-priority_level' is what sorts in descending order.
        Filtering the object to remove anything from the donor list that would have a priority level 1 which is near full capacity. 
        """
        from .models import Item

        missing_prices = Item.objects.filter(estimated_price__isnull=True)
        for item in missing_prices:
            logger.error(f'Item {item.name} hidden: Price is missing.')

        return Item.objects.filter(priority_level__gt=1).exclude(estimated_price=None).order_by('-priority_level')
    
    def get_items_with_name_price_image(self): 
        """Grabs all item objects in database. Iterates through these items and appends the desired information to a 
           list named 'result'."""
        items = self.get_prioritized_items()

        result = []

        for item in items:
            # name, price, image = amazon_api._parse_results(session, item)
            # I don't think we need the above code until we start updating values and create api time logic calls.
            # Perhaps the same situation with a session parameter. 

            result.append({'id': item.pk,
                           'name': item.name,
                           'quantity': item.quantity,  # will get rid of this before production. 
                           'priority': item.priority_level, # Will get rid of this before production. 
                           'price': item.estimated_price,
                           'image': item.amazon_image_url,
                           'amazon_wishlist_url': item.amazon_wishlist_url,
                           })
        return result 


# Adding logic to DonationCart class.
class DonationCart: 
    """DonationCart class handles the creation of session storage as a dictionary object called 'cart'. We use the item_id
       as the key in the key value pair. Values are the objects that we wis to display in the cart html.  """
    def add_item_to_session_cart(self, session, item_id, quantity):
        """I believe sessions are something that Django runs in the background. We pass an id as a parameter and name it item_id.
           This gets used to retrieve that specific item as 'item' object. The ID gets converted to str for cart dict key use. """
        from .models import Item
        # Create the session cart object
        cart = session.get('cart', {})
        item = get_object_or_404(Item, id=item_id)
        
        maxed_out = False
        str_id = str(item_id)

        if str_id in cart:
            cart[str_id]['quantity'] += int(quantity)

        else:
            cart[str_id] = {
                'name': item.name,
                'image': item.amazon_image_url,
                'quantity': int(quantity),
                'price': item.estimated_price
            }
        
        qty_diff = max(0, item.max_quantity - item.quantity)

        if cart[str_id]['quantity'] > qty_diff:
            cart[str_id]['quantity'] = qty_diff
            maxed_out = True

        session['cart'] = cart
        session.modified = True  # This line of code tells Django that the dictionary was changed.
        

        if maxed_out:
            user_message = f"We only need {qty_diff} more of {item.name} at this time."
        else:    
            user_message = f'Succesfully added {int(quantity)} {cart[str_id]['name']}'

        return user_message

    def delete_item_from_session_cart(self, session, item_id):
        """
        Using a Django established session, we will take the item_id parameter given and attempt to remove it from the 
        session cart 'cart'. user_message provides an informative string that will be displayed at the top of the page."""
        cart = session.get('cart', {})
        str_id = str(item_id)

        # Pop the item directly from the cart dictionary
        # Second argument is provided as a fall back so app doesn't crash if id is missing.
        item_data = cart.pop(str_id, None)

        if item_data:
            user_message = f'Succesfully removed {item_data['name']} from cart.'
        else:
            user_message = 'Item was not in your cart.'
        
        session['cart'] = cart
        session.modified = True
        
        return user_message

class AmazonApi:
    """ serpApi will be used to parse product information into variables. """
    SERPAPI_KEY = settings.SERPAPI_KEY
    def __init__(self):
        self.client = serpapi.Client(api_key=self.SERPAPI_KEY)
    
    
    def extract_asin(self, url):
        """ Extract ASIN from Amazon URL."""
        if not url:
            return None
        
        match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
        
        match = re.search(r'/product/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
        
        return None
    
    
    def get_product_info(self, asin):
        """Searches SerpApi to get a json of the product information on the product display"""
        if not asin:
            return None
        
        try:
            results = self.client.search({
                "engine": "amazon_product",
                "asin": asin,
                "amazon_domain": "amazon.com"
            })
            return self._parse_results(results)
        except Exception:
            # This prevents a server crash.
            logger.exception(f'SerpApi Connection Error for ASIN: {asin}') 
            return None

    def _parse_results(self, results):
        """Retrieves name, price and image listed in the product_results dictionary"""
        product = results.get('product_results', {})

        return {
            'name': product.get('title'),
            'price': product.get('extracted_price'),
            'image': self._get_main_image(product),
        }

    def _get_main_image(self, product):
        """Grabs the first image in the image slide. If none exists it defaults to the thumbnail"""
        images = product.get('thumbnails', [])
        return images[0] if images else product.get('thumbnail') 