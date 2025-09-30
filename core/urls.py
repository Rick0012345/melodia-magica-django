from django.urls import path
from . import views

urlpatterns = [
    # Páginas principais
    path('', views.HomeView.as_view(), name='home'),
    path('menu/', views.MenuView.as_view(), name='menu'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('servicos/', views.ServicosView.as_view(), name='servicos'),
    path('contato/', views.ContatoView.as_view(), name='contato'),
    path('login/', views.LoginView.as_view(), name='login'),
    
    # Quiz e jogos
    path('niveis/', views.NiveisView.as_view(), name='niveis'),
    path('quiz/niveis/', views.NiveisView.as_view(), name='quiz_niveis'),
    path('game/<int:quiz_id>/', views.GamePageView.as_view(), name='game_page'),
    
    # Gerenciamento de quizzes e perguntas (views existentes)
    path('quizzes/', views.QuizListView.as_view(), name='quiz_list'),
    path('quiz/criar/', views.QuizCreateView.as_view(), name='quiz_create'),
    path('quiz/<int:pk>/editar/', views.QuizUpdateView.as_view(), name='quiz_update'),
    path('quiz/<int:quiz_id>/perguntas/', views.PerguntaListView.as_view(), name='pergunta_list'),
    path('quiz/<int:quiz_id>/pergunta/criar/', views.PerguntaCreateView.as_view(), name='pergunta_create'),
    path('pergunta/<int:pk>/editar/', views.PerguntaUpdateView.as_view(), name='pergunta_update'),
    path('pergunta/<int:pk>/excluir/', views.PerguntaDeleteView.as_view(), name='pergunta_delete'),
    path('quiz/<int:quiz_id>/validar/', views.PerguntaValidateView.as_view(), name='pergunta_validate'),
    
    # Views otimizadas com templates modernos
    path('quiz/criar-otimizado/', views.QuizCreateOptimizedView.as_view(), name='quiz_create_optimized'),
    path('quiz/<int:quiz_id>/pergunta/criar-otimizada/', views.PerguntaCreateOptimizedView.as_view(), name='pergunta_create_optimized'),
    path('pergunta/<int:pergunta_id>/alternativa/criar-otimizada/', views.AlternativaCreateOptimizedView.as_view(), name='alternativa_create_optimized'),
    
    # Importação de perguntas
    path('importar-perguntas/', views.ImportarPerguntasView.as_view(), name='importar_perguntas'),
    path('quiz/<int:quiz_id>/importar-perguntas/', views.ImportarPerguntasView.as_view(), name='importar_perguntas_quiz'),
    path('download-template/', views.DownloadTemplateView.as_view(), name='download_template'),
]
