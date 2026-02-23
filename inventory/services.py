from .models import Item
from random import uniform

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
    
    def get_items_with_prices(self):
        simulator = PriceSimulator()
        items = self.get_prioritized_items()

        result = []

        for item in items:
            vendor, price = simulator.get_lowest_price(item)

            result.append({'id': item.id,
                           'name': item.items,
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
        str_id = str(item_id)

        if str_id in cart:
            cart[str_id] += int(quantity)
        else:
            cart[str_id] = int(quantity)

        session['cart'] = cart
        session.modified = True  # This line of code tells Django that the dictionary was changed.


class PriceSimulator:
    """
    This will generate simulated prices for three 'Vendors' setting a lower range of the unit_price * 0.7 
    and an upper range of the unit_price * 1.3. Returns a dictionary 'prices' with the vendor: price. 
    """


    VENDORS = ['Amazon', 'Walmart', 'Target']


    def generate_vendor_prices(self, item):
        prices = {}

        for vendor in self.VENDORS:
            price = uniform(item.unit_price * 0.7, item.unit_price * 1.3)

            prices[vendor] = round(price, 2)

        return prices 


    def get_lowest_price(self, item):
        prices = self.generate_vendor_prices(item)
        vendor = min(prices, key=prices.get)
        return vendor, prices[vendor]

class DonationCart:
    pass