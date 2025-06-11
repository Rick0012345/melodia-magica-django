from django.urls import path
from .views import (
    HomeView, 
    NiveisView, 
    GamePageView, 
    CadastrarQuestoesView,
    ServicosView,
    ContatoView,
    LoginView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('servicos/', ServicosView.as_view(), name='servicos'),
    path('contato/', ContatoView.as_view(), name='contato'),
    path('login/', LoginView.as_view(), name='login'),
    path("quiz/niveis/", NiveisView.as_view(), name="niveis"),
    path("quiz/game/", GamePageView.as_view(), name="game_page"),
    path("quiz/cadastrar-questoes/", CadastrarQuestoesView.as_view(), name="cadastrar_questoes"),
]
