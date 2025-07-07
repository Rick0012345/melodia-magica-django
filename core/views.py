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
from django.core.mail import send_mail
from django.conf import settings
from .models import Quiz, Pergunta, Alternativa, Pontuacao
from django.http import HttpResponse
from django.middleware.csrf import get_token



class HomeView(TemplateView):
    template_name = "core/index.html"

class ServicosView(TemplateView):
    template_name = "core/servicos.html"

class ContatoView(TemplateView):
    template_name = "core/contato.html"
    
    def post(self, request, *args, **kwargs):
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')
        
        # Validação básica
        if not all([nome, email, assunto, mensagem]):
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return self.get(request, *args, **kwargs)
        
        try:
            # Aqui você pode implementar o envio de email
            # Por enquanto, vamos apenas simular o envio
            subject = f'Contato via site: {assunto}'
            message = f"""
            Nova mensagem de contato:
            
            Nome: {nome}
            Email: {email}
            Assunto: {assunto}
            
            Mensagem:
            {mensagem}
            """
            
            # Se você tiver configurado o email no settings.py, descomente estas linhas:
            # send_mail(
            #     subject,
            #     message,
            #     email,
            #     [settings.DEFAULT_FROM_EMAIL],
            #     fail_silently=False,
            # )
            
            messages.success(request, 'Mensagem enviada com sucesso! Entraremos em contato em breve.')
            
        except Exception as e:
            messages.error(request, 'Erro ao enviar mensagem. Tente novamente mais tarde.')
        
        return redirect('contato')

class LoginView(TemplateView):
    template_name = "core/login.html"

class MenuView(TemplateView):
    template_name = "core/menu.html"
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        return super().dispatch(request, *args, **kwargs)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "core/profile.html"
    login_url = 'account_login'

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
        
        # Sempre resetar o quiz quando carregar a página pela primeira vez (GET normal)
        # Inicializar variáveis de sessão
        self.request.session['quiz_iniciado'] = True
        self.request.session['pontuacao'] = 0
        self.request.session['acertos'] = 0
        self.request.session['erros'] = 0
        self.request.session['pergunta_atual'] = 0
        self.request.session['quiz_finalizado'] = False
        
        # Obter primeira pergunta (sempre começar do início quando carregar via GET)
        perguntas = list(quiz.perguntas.all().order_by('id'))
        pergunta = perguntas[0] if perguntas else None
        progresso = (1 / len(perguntas)) * 100 if perguntas else 0
        
        context.update({
            'quiz': quiz,
            'pergunta': pergunta,
            'pontuacao': self.request.session.get('pontuacao', 0),
            'acertos': self.request.session.get('acertos', 0),
            'erros': self.request.session.get('erros', 0),
            'progresso': progresso
        })
        
        return context

    def post(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        pergunta_id = request.POST.get('pergunta_id')
        resposta = request.POST.get('resposta')
        
        if not pergunta_id or not resposta:
            return self.get(request, *args, **kwargs)
        
        # Obter pergunta
        pergunta = get_object_or_404(Pergunta, id=pergunta_id)
        
        # Verificar resposta
        acerto = False
        if pergunta.tipo == 'multipla_escolha':
            alternativa_correta = pergunta.alternativas.filter(correta=True).first()
            if alternativa_correta and str(alternativa_correta.id) == resposta:
                acerto = True
        elif pergunta.tipo == 'verdadeiro_falso':
            if resposta.lower() == 'true':
                acerto = True
            else:
                acerto = False
        
        # Atualizar estatísticas
        if acerto:
            request.session['pontuacao'] = request.session.get('pontuacao', 0) + 1
            request.session['acertos'] = request.session.get('acertos', 0) + 1
        else:
            request.session['erros'] = request.session.get('erros', 0) + 1
        
        # Avançar para próxima pergunta
        pergunta_atual = request.session.get('pergunta_atual', 0)
        perguntas = list(quiz.perguntas.all().order_by('id'))
        
        if pergunta_atual + 1 < len(perguntas):
            # Ainda há perguntas
            request.session['pergunta_atual'] = pergunta_atual + 1
            proxima_pergunta = perguntas[pergunta_atual + 1]
            progresso = ((pergunta_atual + 2) / len(perguntas)) * 100
            
            # Retornar próxima pergunta para HTMX
            context = {
                'quiz': quiz,
                'pergunta': proxima_pergunta,
                'pontuacao': request.session.get('pontuacao', 0),
                'acertos': request.session.get('acertos', 0),
                'erros': request.session.get('erros', 0),
                'progresso': progresso
            }
            
            html = f'''
            <div class="question-card" data-acertos="{context['acertos']}" data-erros="{context['erros']}" data-pontos="{context['pontuacao']}" data-progresso="{context['progresso']}">
                <h2 class="question-title">{proxima_pergunta.pergunta}</h2>
                
                <form hx-post="/quiz/game/{quiz.id}/" 
                      hx-target="#question-area" 
                      hx-swap="innerHTML"
                      hx-indicator="#loading">
                                            <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                    <input type="hidden" name="pergunta_id" value="{proxima_pergunta.id}">
            '''
            
            if proxima_pergunta.tipo == 'multipla_escolha':
                for alternativa in proxima_pergunta.alternativas.all():
                    html += f'''
                    <label class="answer-option">
                        <input type="radio" name="resposta" value="{alternativa.id}" required>
                        <span class="answer-text">{alternativa.texto}</span>
                    </label>
                    '''
            elif proxima_pergunta.tipo == 'verdadeiro_falso':
                html += '''
                <label class="answer-option">
                    <input type="radio" name="resposta" value="true" required>
                    <span class="answer-text">Verdadeiro</span>
                </label>
                <label class="answer-option">
                    <input type="radio" name="resposta" value="false" required>
                    <span class="answer-text">Falso</span>
                </label>
                '''
            
            html += '''
                    <button type="submit" class="submit-btn">
                        Responder
                        <div class="loading-spinner" id="loading">
                            <i class="fas fa-spinner fa-spin"></i>
                        </div>
                    </button>
                </form>
            </div>
            '''
            
            return HttpResponse(html)
        
        else:
            # Quiz finalizado
            request.session['quiz_finalizado'] = True
            
            # Salvar pontuação no banco
            if request.user.is_authenticated:
                Pontuacao.objects.update_or_create(
                    usuario=request.user,
                    quiz=quiz,
                    defaults={'pontuacao': request.session.get('pontuacao', 0)}
                )
            
            # Retornar resultado
            pontuacao = request.session.get('pontuacao', 0)
            acertos = request.session.get('acertos', 0)
            erros = request.session.get('erros', 0)
            
            html = f'''
            <div class="result-container">
                <h2 class="result-title">🎉 Quiz Finalizado!</h2>
                
                <div class="result-card">
                    <div class="result-stats">
                        <div class="result-stat success">
                            <div class="result-stat-value">{acertos}</div>
                            <div class="result-stat-label">Acertos</div>
                        </div>
                        <div class="result-stat danger">
                            <div class="result-stat-value">{erros}</div>
                            <div class="result-stat-label">Erros</div>
                        </div>
                        <div class="result-stat warning">
                            <div class="result-stat-value">{pontuacao}</div>
                            <div class="result-stat-label">Pontos</div>
                        </div>
                    </div>
                    
                    <div class="result-buttons">
                        <a href="/quiz/niveis/" class="btn-secondary">
                            <i class="fas fa-arrow-left"></i> Voltar aos Níveis
                        </a>
                        <button hx-get="/quiz/game/{quiz.id}/?reiniciar=true" 
                                hx-target="#question-area" 
                                hx-swap="innerHTML"
                                class="btn-primary">
                            <i class="fas fa-redo"></i> Jogar Novamente
                        </button>
                    </div>
                </div>
            </div>
            '''
            
            return HttpResponse(html)

    def get(self, request, *args, **kwargs):
        # Verificar se quer reiniciar
        if request.GET.get('reiniciar') == 'true':
            # Limpar sessão
            request.session.pop('quiz_iniciado', None)
            request.session.pop('pontuacao', None)
            request.session.pop('acertos', None)
            request.session.pop('erros', None)
            request.session.pop('pergunta_atual', None)
            request.session.pop('quiz_finalizado', None)
            
            # Retornar primeira pergunta para HTMX
            quiz_id = self.kwargs.get('quiz_id')
            quiz = get_object_or_404(Quiz, id=quiz_id)
            primeira_pergunta = quiz.perguntas.first()
            
            if primeira_pergunta:
                html = f'''
                <div class="question-card" data-acertos="0" data-erros="0" data-pontos="0" data-progresso="0">
                    <h2 class="question-title">{primeira_pergunta.pergunta}</h2>
                    
                    <form hx-post="/quiz/game/{quiz.id}/" 
                          hx-target="#question-area" 
                          hx-swap="innerHTML"
                          hx-indicator="#loading">
                                                 <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        <input type="hidden" name="pergunta_id" value="{primeira_pergunta.id}">
                '''
                
                if primeira_pergunta.tipo == 'multipla_escolha':
                    for alternativa in primeira_pergunta.alternativas.all():
                        html += f'''
                        <label class="answer-option">
                            <input type="radio" name="resposta" value="{alternativa.id}" required>
                            <span class="answer-text">{alternativa.texto}</span>
                        </label>
                        '''
                elif primeira_pergunta.tipo == 'verdadeiro_falso':
                    html += '''
                    <label class="answer-option">
                        <input type="radio" name="resposta" value="true" required>
                        <span class="answer-text">Verdadeiro</span>
                    </label>
                    <label class="answer-option">
                        <input type="radio" name="resposta" value="false" required>
                        <span class="answer-text">Falso</span>
                    </label>
                    '''
                
                html += '''
                        <button type="submit" class="submit-btn">
                            Responder
                            <div class="loading-spinner" id="loading">
                                <i class="fas fa-spinner fa-spin"></i>
                            </div>
                        </button>
                    </form>
                </div>
                '''
                
                return HttpResponse(html)
        
        return super().get(request, *args, **kwargs)
    