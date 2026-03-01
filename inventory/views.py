from django.shortcuts import render, redirect, get_object_or_404
from .services import InventoryLogic
from .models import Item
# Create your views here.

def item_list(request):
    #items = Item.objects.order_by('items')
    logic = InventoryLogic()
    items = logic.get_items_with_prices()
    return render(request, 'inventory/item_list.html', {'items': items})

# new testing
def add_to_cart(request, item_id):
    if request.method == "POST":
        qty_str = request.POST.get('quantity', '1')

        # Exception handling to prevent string literal input
        try:
            quantity = int(qty_str)
        except ValueError:
            quantity = 1
        
        logic = InventoryLogic()
        logic.add_item_to_session_cart(request.session, item_id, quantity)

    return redirect('item_list')


# new testing
def view_cart(request):
    """
    grabs the cart dictionary from the session created in add_to_cart().
    Then iterates through the session data using a for loop. In the loop 
    it grabs the category, item, quantity, unit price and line total.
    Grand total is calculated at the end.

    get('cart', {}) is saying i want the cart session (which is a dictionary) and if there is not a dictionary yet the default is an empty dictionary.
    """
    cart_session = request.session.get('cart', {})

    cart_items = []
    grand_total_items = 0 # this probably calculates the total number of items not the total expense.


# remember that .items() grabs the key value pair of a a dictionary in this case the 'cart' dictionary cart_session
    for item_id, quantity in cart_session.items():
        try:
            # Attempts to grab the Item object from the database.
            item = Item.objects.get(id=item_id)
            cart_items.append({
                'item': item, 
                'quantity': quantity,
            })
            grand_total_items += int(quantity)
        except Item.DoesNotExist:
            # And if the item object is not in the database...
            continue

    context = {
        'cart_items': cart_items,
        'total_count': grand_total_items
    }
    return render(request, 'inventory/donation_cart.html', context)