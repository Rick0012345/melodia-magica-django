from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    FormView,
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
    PermissionRequiredMixin,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Quiz, Pergunta, Alternativa, Pontuacao



class HomeView(TemplateView):
    template_name = "core/index.html"

class ServicosView(TemplateView):
    template_name = "core/servicos.html"

class ContatoView(TemplateView):
    template_name = "core/contato.html"

class LoginView(TemplateView):
    template_name = "core/login.html"

class MenuView(TemplateView):
    template_name = "core/menu.html"
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        return super().dispatch(request, *args, **kwargs)

class NiveisView(TemplateView):
    template_name = "core/niveis.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quizzes"] = Quiz.objects.all().order_by('nivel_dificuldade')
        return context

class GamePageView(TemplateView):
    template_name = "core/game.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Verifica se o quiz está finalizado
        quiz_finalizado = self.request.session.get('quiz_finalizado', False)
        
        if quiz_finalizado:
            context['quiz'] = quiz
            context['pergunta'] = None
            context['pontuacao'] = self.request.session.get('pontuacao', 0)
            context['acertos'] = self.request.session.get('acertos', 0)
            context['erros'] = self.request.session.get('erros', 0)
            return context
        
        # Pega a pergunta atual ou a primeira pergunta
        pergunta_atual_id = self.request.session.get('pergunta_atual_id')
        if pergunta_atual_id:
            pergunta = get_object_or_404(Pergunta, id=pergunta_atual_id)
        else:
            pergunta = quiz.perguntas.first()
        
        # Calcula o progresso
        total_perguntas = quiz.perguntas.count()
        if pergunta_atual_id:
            perguntas_respondidas = quiz.perguntas.filter(id__lte=pergunta_atual_id).count()
            progresso = (perguntas_respondidas / total_perguntas) * 100
        else:
            progresso = 0
        
        context['quiz'] = quiz
        context['pergunta'] = pergunta
        context['progresso'] = progresso
        context['pontuacao'] = self.request.session.get('pontuacao', 0)
        context['acertos'] = self.request.session.get('acertos', 0)
        context['erros'] = self.request.session.get('erros', 0)
        return context

    def post(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id)
        resposta = request.POST.get('resposta')
        pergunta_atual_id = request.POST.get('pergunta_atual_id')
        
        # Verifica a resposta
        pergunta_atual = get_object_or_404(Pergunta, id=pergunta_atual_id)
        pontuacao = request.session.get('pontuacao', 0)
        acertos = request.session.get('acertos', 0)
        erros = request.session.get('erros', 0)
        
        if pergunta_atual.tipo == 'multipla_escolha':
            alternativa_correta = pergunta_atual.alternativas.filter(correta=True).first()
            if alternativa_correta and str(alternativa_correta.id) == resposta:
                pontuacao += 1
                acertos += 1
            else:
                erros += 1
        elif pergunta_atual.tipo == 'verdadeiro_falso':
            alternativa_correta = pergunta_atual.alternativas.filter(correta=True).first()
            if alternativa_correta and str(alternativa_correta.correta).lower() == resposta:
                pontuacao += 1
                acertos += 1
            else:
                erros += 1
        
        request.session['pontuacao'] = pontuacao
        request.session['acertos'] = acertos
        request.session['erros'] = erros
        
        # Pega a próxima pergunta
        proxima_pergunta = quiz.perguntas.filter(id__gt=pergunta_atual_id).order_by('id').first()
        
        if proxima_pergunta:
            request.session['pergunta_atual_id'] = proxima_pergunta.id
            return redirect('game_page', quiz_id=quiz_id)
        else:
            # Quiz finalizado - salva a pontuação no banco
            if request.user.is_authenticated:
                Pontuacao.objects.update_or_create(
                    usuario=request.user,
                    quiz=quiz,
                    defaults={'pontuacao': pontuacao}
                )
            
            # Marca o quiz como finalizado
            request.session['quiz_finalizado'] = True
            
            # Redireciona para a mesma página para mostrar os resultados
            return redirect('game_page', quiz_id=quiz_id)

    def get(self, request, *args, **kwargs):
        # Se o quiz estiver finalizado e o usuário clicar em "Voltar aos Níveis"
        if request.session.get('quiz_finalizado', False) and request.GET.get('voltar') == 'true':
            # Limpa a sessão
            request.session.pop('pontuacao', None)
            request.session.pop('acertos', None)
            request.session.pop('erros', None)
            request.session.pop('pergunta_atual_id', None)
            request.session.pop('quiz_finalizado', None)
            
            return redirect('niveis')
        
        return super().get(request, *args, **kwargs)
    