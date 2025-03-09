from django.contrib import admin
from .models import *
# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_active")
    search_fields = ("name", "category", "description")



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "is_active")
    search_fields = ("name", "category", "description")
    list_filter = ("created_at", "category")
    inlines = [ProductImageInline]

@admin.register(ProductImage)
class ProductImageInline(admin.ModelAdmin):
    list_display = ("product", "image")
    search_fields = ("product__name",)