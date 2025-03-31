from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, ReplyToContactView

router = DefaultRouter()
router.register(r'contacts', ContactViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('reply/', ReplyToContactView.as_view(), name='reply_to_contact'),
]
