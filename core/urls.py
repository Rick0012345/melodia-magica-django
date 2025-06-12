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
from . import views

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('servicos/', ServicosView.as_view(), name='servicos'),
    path('contato/', ContatoView.as_view(), name='contato'),
    path('login/', LoginView.as_view(), name='login'),
    path("quiz/niveis/", NiveisView.as_view(), name="niveis"),
    path("quiz/game/<int:quiz_id>/", GamePageView.as_view(), name="game_page"),
    path("quiz/cadastrar-questoes/", CadastrarQuestoesView.as_view(), name="cadastrar_questoes"),
    path('cadastrar-quiz/', views.cadastrar_quiz, name='cadastrar_quiz'),
    path('cadastrar-pergunta/<int:quiz_id>/', views.cadastrar_pergunta, name='cadastrar_pergunta'),
    path('editar-pergunta/<int:pergunta_id>/', views.editar_pergunta, name='editar_pergunta'),
    path('excluir-pergunta/<int:pergunta_id>/', views.excluir_pergunta, name='excluir_pergunta'),
]
