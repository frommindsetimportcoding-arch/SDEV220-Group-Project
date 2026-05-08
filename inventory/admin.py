from django.contrib import admin
from django.utils.html import format_html
from .models import Item

# Register your models here.
# I want to add field sets. but let me not get ahead of myself.

# class ItemAdmin(admin.ModelAdmin)
#     fieldsets = [
#         ("Item Fields", {'fields': ['item', 'category', 'description', ]})
#     ]

@admin.action(description='Fetch Amazon info for selected items')
def fetch_amazon_data(self, request, queryset):
    """ Queryset is built by selecting items in the admin panel via checkbox. We then iterate through each item object
        and run the save() method again which will refresh the API values in the item object (name, price, image). """
    for item in queryset:
        item.save()
    self.message_user(request, f'Successfully triggered updates for {queryset.count()} items.')
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """ Allows for custom logic in the admin. list_display allows us to see row values of fields on the main page of admin.
        Actions lets us add functionality to the drop down, in this case we are adding the fetch_amazon_data() method. """
    list_display = ('name', 'display_image', 'priority_level', 'quantity', 'estimated_price')
    actions = [fetch_amazon_data]


    def display_image(self, obj):
        """ Renders the image in a safe html format that Django is happy with."""
        if obj.amazon_image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain;" />', obj.amazon_image_url)
        return "No Image"
    
    # This assigns a descriptive name to the display_image method that is more presentable in list_display.
    display_image.short_description = 'Product Image'
    