"""
Views handle the logic needed to process and capture the objects required for the html UI.
"""
from django.shortcuts import render, redirect, get_object_or_404
from .services import DonationCart, InventoryLogic
from .models import Item
from django.http import HttpRequest
from django.contrib import messages
import logging
import re


logger = logging.getLogger(__name__)
DJANGO_MAX_INT = 2147482647
# Create your views here.

def item_list(request: HttpRequest):
    """
    Users the InventoryLogic() class to grab the items which will be displayed in item_list.html
    """
    #items = Item.objects.order_by('items')  <-- No longer needed. Not ready to delete though. 
    logic = InventoryLogic()
    items = logic.get_items_with_name_price_image()
    # Grabbing the first item so that I can use the wishlist URL without iteration.
    first_item = items[0] if items else None

    context = {
        'items': items,
        'first_item': first_item,
    }
    return render(request, 'inventory/item_list.html', context)


def remove_from_cart(request: HttpRequest, item_id):
    """Function grabs the item_id from the Item object to check to make sure that the ID still exists. 
       Then it relates the cart object to the session saved in cookies and removes the item determined by the primary key."""
    item = get_object_or_404(Item, pk=item_id)

    cart = DonationCart()

    message_output = cart.delete_item_from_session_cart(request.session, item.pk)

    messages.success(request, message_output)

    return redirect('view_cart')


def add_to_cart(request: HttpRequest, item_id):
    """Function checks for item_id exisence first to avoid crash. Explicitly checks for "POST" to reduce attack surface.
       Then checks for the value 'quantity' otherwise defaults to an integer 1. To be safe, we handle the exception by checking
       for a ValueError and forcing the quantity to 1 to continue. add_item_to_session_cart creates a session dictionary if one
       does not exist, otherwise it updates the dictionary."""
    item = get_object_or_404(Item, pk=item_id)
    user_ip = request.META.get('REMOTE_ADDR')

    if request.method == "POST":
        
        qty_str = request.POST.get('quantity', '1')

        # Exception handling to prevent string literal input
        try:
            # First check on overflow or undesired input.
            if len(qty_str) > 7:
                logger.error(f"SECURITY: Excessively long input received: {qty_str[:20]}... | IP: {user_ip} | Value: '{qty_str}'")
                messages.error(request, "Invalid quantity entered")
                return redirect('item_list')

            # Resists negative values.
            quantity = max(1, int(qty_str))
            
        except ValueError:
            injection_patterns = r"[<>{};\"']"

            if re.search(injection_patterns, qty_str):
                # INJECTION ATTEMPT
                logger.error(
                    f"SECURITY: Potential Injection Attempt | IP: {user_ip} | Value: '{qty_str}'"
                )
            else:
                # Typo
                logger.warning(
                    f"INVALID DATA: Bypassed Frontend Validation | IP: {user_ip} | Value: '{qty_str}'"
                )
            messages.error(request, "There was an error with your donation quantity.")
            return redirect('item_list')
        
        cart = DonationCart()

        message_output = cart.add_item_to_session_cart(request.session, item.pk, quantity)

        messages.success(request, message_output)

    return redirect('item_list')



def view_cart(request: HttpRequest):
    """
    grabs the cart dictionary from the session created in add_to_cart().
    Then iterates through the session data using a for loop. In the loop 
    it grabs the category, item, quantity, unit price and line total.
    Grand total is calculated at the end.

    get('cart', {}) is saying i want the cart session (which is a dictionary) and if there is not a dictionary yet the default is an empty dictionary.
    """
    cart_session = request.session.get('cart', {})

    cart_items = []
    grand_total = 0 

    for item_id, data in cart_session.items():
        try:
            # Attempts to grab the Item object from the database.
            item = Item.objects.get(id=item_id)

            if item.estimated_price is None:
                logger.error(f"Cart Calculation Error: Item '{item.name}' (ID: {item_id}) missing price.")
                continue

            line_total = item.estimated_price * data['quantity']
            grand_total += line_total
            cart_items.append({
                'item': item,           # Passes the whole object to the template
                'name': item.name,
                'image': item.amazon_image_url, 
                'quantity': data['quantity'],
                'price': item.estimated_price,
                'line_total': round(line_total, 2)
            })

        except Item.DoesNotExist:
            # And if the item object is not in the database...
            logger.warning(f"Session Cleanup: Item ID {item_id} found in session but not in DB")
            continue
    # Grabbing first item to use the Amazon Wishlist URL.
    first_item = Item.objects.first()

    context = {
        'cart_items': cart_items,
        'grand_total': round(grand_total, 2),
        'first_item': first_item
    }
    return render(request, 'inventory/donation_cart.html', context)