from django.shortcuts import render, redirect, get_object_or_404
from .services import DonationCart, InventoryLogic
from .models import Item
from django.http import HttpRequest
from django.contrib import messages

# Create your views here.

def item_list(request: HttpRequest):
    #items = Item.objects.order_by('items')
    logic = InventoryLogic()
    items = logic.get_items_with_name_price_image()
    return render(request, 'inventory/item_list.html', {'items': items})


def remove_from_cart(request: HttpRequest, item_id):
    cart = DonationCart()

    message_output = cart.delete_item_from_session_cart(request.session, item_id)

    messages.success(request, message_output)

    return redirect('view_cart')


def add_to_cart(request: HttpRequest, item_id):

    if request.method == "POST":
        
        qty_str = request.POST.get('quantity', '1')

        # Exception handling to prevent string literal input
        try:
            quantity = int(qty_str)
        except ValueError:
            quantity = 1
        
        cart = DonationCart()
        cart.add_item_to_session_cart(request.session, item_id, quantity)

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
            continue

    context = {
        'cart_items': cart_items,
        'grand_total': round(grand_total, 2)
    }
    return render(request, 'inventory/donation_cart.html', context)