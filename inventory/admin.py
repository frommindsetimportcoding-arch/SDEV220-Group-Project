from django.contrib import admin
from .models import Item

# Register your models here.
# I want to add field sets. but let me not get ahead of myself.

# class ItemAdmin(admin.ModelAdmin)
#     fieldsets = [
#         ("Item Fields", {'fields': ['item', 'category', 'description', ]})
#     ]
admin.site.register(Item)