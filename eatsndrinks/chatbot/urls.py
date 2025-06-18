from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('history/', views.chat_history, name='chat_history'),
    path('session/create/', views.create_session, name='create_session'),
    path('config/', views.get_config, name='get_config'),
    path('recommendations/', views.quick_recommendations, name='quick_recommendations'),
] 