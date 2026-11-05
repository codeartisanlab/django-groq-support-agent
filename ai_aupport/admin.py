from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'product_name', 'status', 'estimated_delivery')
    search_fields = ('order_number', 'customer_name')