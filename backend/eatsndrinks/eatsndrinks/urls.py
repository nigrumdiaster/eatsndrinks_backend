from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('catalogue/', include('catalogue.urls')),
    
    # Endpoint for generating the OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Endpoint for Swagger UI
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),




]
