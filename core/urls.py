from django.urls import path
from .views import (
    HomeView, 
    NiveisView, 
    GamePageView, 
    ServicosView,
    ContatoView,
    LoginView,
    MenuView,
    ProfileView,

)


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('menu/', MenuView.as_view(), name='menu'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('servicos/', ServicosView.as_view(), name='servicos'),
    path('contato/', ContatoView.as_view(), name='contato'),
    path('login/', LoginView.as_view(), name='login'),
    path("quiz/niveis/", NiveisView.as_view(), name="niveis"),
    path("quiz/game/<int:quiz_id>/", GamePageView.as_view(), name="game_page"),

]
