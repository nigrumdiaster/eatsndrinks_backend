from rest_framework import viewsets

from .mixins import CustomPermissionMixin, CategorySchemaMixin, ProductImageSchemaMixin, ProductSchemaMixin
from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer




# Category ViewSet
class CategoryViewSet(CategorySchemaMixin, CustomPermissionMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get", "post", "put", "patch"]

    


# Product ViewSet
class ProductViewSet(ProductSchemaMixin, CustomPermissionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ["get", "post", "put", "patch"]
    

    
class ProductImageViewSet(ProductImageSchemaMixin, CustomPermissionMixin, viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    http_method_names = ["get", "post", "put", "patch"]

   