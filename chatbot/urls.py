from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('message/', views.chat_message, name='chat_message'),
    path('history/', views.chat_history, name='chat_history'),
] 