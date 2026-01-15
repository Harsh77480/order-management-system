from django.contrib import admin
from .models import  Product, User, Order, OrderItem
admin.site.register(Product) 
admin.site.register(User)
admin.site.register(OrderItem)

class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline] 

admin.site.register(Order, OrderAdmin)