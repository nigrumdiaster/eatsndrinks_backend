from django.contrib import admin
from .models import Cart, CartItem

# Register Cart
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')  # Fields to display in the list view
    search_fields = ('user__username', 'user__email')  # Allow search by username or email
    list_filter = ('user',)  # Add a filter sidebar for users

admin.site.register(Cart, CartAdmin)

# Register CartItem
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')  # Fields to display
    search_fields = ('cart__user__username', 'product__name')  # Search by cart user or product name
    list_filter = ('cart', 'product')  # Add filters for cart and product

admin.site.register(CartItem, CartItemAdmin)
