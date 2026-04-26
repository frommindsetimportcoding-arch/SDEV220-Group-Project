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
    for item in queryset:
        item.save()
    self.message_user(request, f'Successfully triggered updates for {queryset.count()} items.')
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_image', 'priority_level', 'quantity', 'estimated_price')
    actions = [fetch_amazon_data]

    # Renders the image in a safe html format that django is happy with.
    def display_image(self, obj):
        if obj.amazon_image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain;" />', obj.amazon_image_url)
        return "No Image"
    
    display_image.short_description = 'Product Image'
    