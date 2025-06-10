from django.urls import path
from .views import HomeView, NiveisView, GamePageView, CadastrarQuestoesView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path("quiz/niveis/", NiveisView.as_view(), name="niveis"),
    path("quiz/game/", GamePageView.as_view(), name="game_page"),
    path("quiz/cadastrar-questoes/", CadastrarQuestoesView.as_view(), name="cadastrar_questoes"),
]
