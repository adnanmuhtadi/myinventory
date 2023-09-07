from django.contrib import admin
from .forms import StockCreateForm
from .models import *


class StockCreateAdmin(admin.ModelAdmin):
    list_display = ['category', 'item_name', 'quantity']
    form = StockCreateForm
    list_filter = ['category']
    search_fields = ['category', 'item_name']


# Register your models here.
admin.site.register(Stock, StockCreateAdmin)
admin.site.register(StockHistory)
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Room)
admin.site.register(Household)
