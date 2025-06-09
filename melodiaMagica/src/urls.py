from django.urls import path
from . import views

app_name = 'src'

urlpatterns = [
    path('', views.home, name='home'),
] 