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
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.conf import settings
from .models import Quiz, Pergunta, Alternativa, Pontuacao
from .forms import QuizForm, PerguntaForm, PerguntaComAlternativasForm, AlternativaFormSet, AlternativaForm
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
import time
import json
import pandas as pd
import io
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


class HomeView(TemplateView):
    template_name = "core/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona timestamp para quebrar cache do vídeo
        context['timestamp'] = int(time.time())
        return context

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
        
        # Verificar resposta usando o método helper do modelo
        acerto = pergunta.validar_resposta(resposta)
        
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
            
            action_url = reverse('game_page', kwargs={'quiz_id': quiz.id})
            html = f'''
            <div class="question-card" data-acertos="{context['acertos']}" data-erros="{context['erros']}" data-pontos="{context['pontuacao']}" data-progresso="{context['progresso']}">
                <h2 class="question-title">{proxima_pergunta.pergunta}</h2>
                
                <form hx-post="{action_url}" 
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
                action_url = reverse('game_page', kwargs={'quiz_id': quiz.id})
                html = f'''
                <div class="question-card" data-acertos="0" data-erros="0" data-pontos="0" data-progresso="0">
                    <h2 class="question-title">{primeira_pergunta.pergunta}</h2>
                    
                    <form hx-post="{action_url}" 
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


# ===== VIEWS PARA GERENCIAMENTO DE PERGUNTAS =====

class QuizListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Lista todos os quizzes para gerenciamento"""
    model = Quiz
    template_name = 'core/quiz_list.html'
    context_object_name = 'quizzes'
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class QuizCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Criar novo quiz"""
    model = Quiz
    form_class = QuizForm
    template_name = 'core/quiz_form.html'
    success_url = reverse_lazy('quiz_list')
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, 'Quiz criado com sucesso!')
        return super().form_valid(form)

class QuizUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Editar quiz existente"""
    model = Quiz
    form_class = QuizForm
    template_name = 'core/quiz_form.html'
    success_url = reverse_lazy('quiz_list')
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, 'Quiz atualizado com sucesso!')
        return super().form_valid(form)

class QuizDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Deletar quiz"""
    model = Quiz
    template_name = 'core/quiz_confirm_delete.html'
    login_url = 'account_login'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_success_url(self):
        return reverse_lazy('quiz_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Quiz deletado com sucesso!')
        return super().delete(request, *args, **kwargs)

class PerguntaListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Lista perguntas de um quiz específico"""
    model = Pergunta
    template_name = 'core/pergunta_list.html'
    context_object_name = 'perguntas'
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_queryset(self):
        self.quiz = get_object_or_404(Quiz, pk=self.kwargs['quiz_id'])
        return Pergunta.objects.filter(quiz=self.quiz).prefetch_related('alternativas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.quiz
        return context

class PerguntaCreateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Criar nova pergunta com alternativas"""
    template_name = 'core/pergunta_form.html'
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.quiz = get_object_or_404(Quiz, pk=self.kwargs['quiz_id'])
        context['quiz'] = self.quiz
        context['form'] = PerguntaComAlternativasForm(quiz=self.quiz)
        return context
    
    def post(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, pk=self.kwargs['quiz_id'])
        form = PerguntaComAlternativasForm(
            request.POST,
            quiz=self.quiz
        )
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    pergunta = form.save()
                    print(f"SUCESSO: Pergunta salva com ID: {pergunta.id}, Texto: {pergunta.pergunta}")
                    messages.success(request, 'Pergunta criada com sucesso!')
                    return redirect('pergunta_list', quiz_id=self.quiz.id)
            except Exception as e:
                print(f"ERRO ao salvar pergunta: {e}")
                messages.error(request, f'Erro ao salvar pergunta: {str(e)}')
        else:
            print(f"FORMULÁRIO INVÁLIDO: {form.errors}")
            print(f"Erros da pergunta: {form.pergunta_form.errors}")
            print(f"Erros das alternativas: {form.alternativa_formset.errors}")
            messages.error(request, 'Erro ao criar pergunta. Verifique os dados.')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

class PerguntaUpdateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Editar pergunta existente"""
    template_name = 'core/pergunta_form.html'
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.pergunta = get_object_or_404(Pergunta, pk=self.kwargs['pk'])
        self.quiz = self.pergunta.quiz
        context['quiz'] = self.quiz
        context['pergunta'] = self.pergunta
        context['form'] = PerguntaComAlternativasForm(
            pergunta_instance=self.pergunta,
            quiz=self.quiz
        )
        return context
    
    def post(self, request, *args, **kwargs):
        self.pergunta = get_object_or_404(Pergunta, pk=self.kwargs['pk'])
        self.quiz = self.pergunta.quiz
        
        form = PerguntaComAlternativasForm(
            request.POST,
            pergunta_instance=self.pergunta,
            quiz=self.quiz
        )
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    pergunta = form.save()
                    messages.success(request, 'Pergunta atualizada com sucesso!')
                    return redirect('pergunta_list', quiz_id=self.quiz.id)
            except Exception as e:
                messages.error(request, f'Erro ao atualizar pergunta: {str(e)}')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

class PerguntaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Deletar pergunta"""
    model = Pergunta
    template_name = 'core/pergunta_confirm_delete.html'
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_success_url(self):
        return reverse_lazy('pergunta_list', kwargs={'quiz_id': self.object.quiz.id})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Pergunta deletada com sucesso!')
        return super().delete(request, *args, **kwargs)

class PerguntaValidateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Validar perguntas de um quiz"""
    template_name = 'core/pergunta_validate.html'
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.quiz = get_object_or_404(Quiz, pk=self.kwargs['quiz_id'])
        perguntas = self.quiz.perguntas.prefetch_related('alternativas')
        
        # Validar cada pergunta
        perguntas_validacao = []
        for pergunta in perguntas:
            validacao = {
                'pergunta': pergunta,
                'valida': pergunta.is_questao_valida(),
                'problemas': []
            }
            
            if pergunta.tipo == 'multipla_escolha':
                total_alternativas = pergunta.total_alternativas()
                alternativas_corretas = pergunta.alternativas.filter(correta=True).count()
                
                if total_alternativas < 2:
                    validacao['problemas'].append('Deve ter pelo menos 2 alternativas')
                if alternativas_corretas != 1:
                    validacao['problemas'].append('Deve ter exatamente 1 alternativa correta')
            
            elif pergunta.tipo == 'verdadeiro_falso':
                if pergunta.resposta_verdadeiro_falso is None:
                    validacao['problemas'].append('Deve definir se a resposta correta é Verdadeiro ou Falso')
            
            perguntas_validacao.append(validacao)
        
        context['quiz'] = self.quiz
        context['perguntas_validacao'] = perguntas_validacao
        context['total_perguntas'] = len(perguntas_validacao)
        context['perguntas_validas'] = sum(1 for p in perguntas_validacao if p['valida'])
        
        return context


# Views otimizadas com templates modernos
class QuizCreateOptimizedView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View otimizada para criar quiz com template moderno"""
    model = Quiz
    form_class = QuizForm
    template_name = 'core/quiz_create_optimized.html'
    success_url = reverse_lazy('quiz_list')
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Quiz "{self.object.titulo}" criado com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Criar Novo Quiz'
        return context

class PerguntaCreateOptimizedView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Criar nova pergunta com template otimizado"""
    template_name = 'core/pergunta_create_optimized.html'
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'quiz_id' in self.kwargs:
            context['quiz'] = get_object_or_404(Quiz, id=self.kwargs['quiz_id'])
            context['form'] = PerguntaForm()
        return context
    
    def post(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=self.kwargs['quiz_id'])
        
        try:
            with transaction.atomic():
                # Criar pergunta
                tipo = request.POST.get('tipo')
                resposta_vf = None
                
                # Processar resposta verdadeiro/falso
                if tipo == 'verdadeiro_falso':
                    resposta_vf_raw = request.POST.get('resposta_verdadeiro_falso')
                    if resposta_vf_raw == 'true':
                        resposta_vf = True
                    elif resposta_vf_raw == 'false':
                        resposta_vf = False
                
                pergunta = Pergunta.objects.create(
                    pergunta=request.POST.get('pergunta'),
                    quiz=quiz,
                    tipo=tipo,
                    resposta_verdadeiro_falso=resposta_vf
                )
                
                # Processar alternativas para múltipla escolha
                if pergunta.tipo == 'multipla_escolha':
                    alternativa_correta = request.POST.get('alternativa_correta')
                    
                    for i in range(1, 7):  # Máximo 6 alternativas
                        alternativa_texto = request.POST.get(f'alternativa_{i}')
                        if alternativa_texto and alternativa_texto.strip():
                            Alternativa.objects.create(
                                pergunta=pergunta,
                                texto=alternativa_texto.strip(),
                                correta=(str(i) == alternativa_correta)
                            )
                
                messages.success(request, 'Questão criada com sucesso!')
                return redirect('pergunta_list', quiz_id=quiz.id)
                
        except Exception as e:
            messages.error(request, f'Erro ao criar questão: {str(e)}')
            
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class AlternativaCreateOptimizedView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View otimizada para criar alternativa com template moderno"""
    model = Alternativa
    form_class = AlternativaForm
    template_name = 'core/alternativa_create_optimized.html'
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_success_url(self):
        return reverse_lazy('alternativa_list', kwargs={'pergunta_id': self.object.pergunta.id})
    
    def form_valid(self, form):
        if 'pergunta_id' in self.kwargs:
            form.instance.pergunta_id = self.kwargs['pergunta_id']
        response = super().form_valid(form)
        messages.success(self.request, 'Alternativa criada com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'pergunta_id' in self.kwargs:
            pergunta = get_object_or_404(Pergunta, id=self.kwargs['pergunta_id'])
            context['pergunta'] = pergunta
            context['alternativas'] = pergunta.alternativas.all()
        return context


class ImportarPerguntasView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View para importar perguntas de planilhas Excel/CSV"""
    template_name = 'core/importar_perguntas.html'
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_id = self.kwargs.get('quiz_id')
        if quiz_id:
            context['quiz'] = get_object_or_404(Quiz, id=quiz_id)
        else:
            context['quizzes'] = Quiz.objects.all().order_by('-data_criacao')
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            # Verificar se foi enviado um arquivo
            if 'arquivo' not in request.FILES:
                messages.error(request, 'Por favor, selecione um arquivo para importar.')
                return self.get(request, *args, **kwargs)
            
            arquivo = request.FILES['arquivo']
            quiz_id = request.POST.get('quiz_id')
            
            # Validar quiz
            if not quiz_id:
                messages.error(request, 'Por favor, selecione um quiz.')
                return self.get(request, *args, **kwargs)
            
            quiz = get_object_or_404(Quiz, id=quiz_id)
            
            # Validar tipo de arquivo
            if not arquivo.name.endswith(('.xlsx', '.xls', '.csv')):
                messages.error(request, 'Formato de arquivo não suportado. Use Excel (.xlsx, .xls) ou CSV.')
                return self.get(request, *args, **kwargs)
            
            # Processar arquivo
            resultado = self.processar_planilha(arquivo, quiz)
            
            if resultado['sucesso']:
                messages.success(
                    request, 
                    f'Importação concluída! {resultado["importadas"]} perguntas importadas com sucesso.'
                )
                if resultado['erros']:
                    messages.warning(
                        request,
                        f'{len(resultado["erros"])} linhas com erro foram ignoradas. Verifique o formato.'
                    )
                return redirect('pergunta_list', quiz_id=quiz.id)
            else:
                messages.error(request, f'Erro na importação: {resultado["erro"]}')
                return self.get(request, *args, **kwargs)
                
        except Exception as e:
            messages.error(request, f'Erro inesperado: {str(e)}')
            return self.get(request, *args, **kwargs)
    
    def processar_planilha(self, arquivo, quiz):
        """Processa a planilha e importa as perguntas"""
        try:
            # Ler arquivo
            if arquivo.name.endswith('.csv'):
                df = pd.read_csv(arquivo, encoding='utf-8')
            else:
                df = pd.read_excel(arquivo)
            
            # Normalizar e mapear cabeçalhos para aceitar formatos alternativos
            def _norm(s):
                return str(s).strip().lower().replace(' ', '_').replace('-', '_')

            # Mapa de colunas encontradas (normalizado -> original)
            norm_to_orig = { _norm(col): col for col in df.columns }

            # Construir mapa de renomeações para o formato canônico
            rename_map = {}
            # Pergunta e tipo
            for cand in ['pergunta', 'questao', 'questão']:
                if cand in norm_to_orig:
                    rename_map[norm_to_orig[cand]] = 'pergunta'
                    break
            if 'tipo' in norm_to_orig:
                rename_map[norm_to_orig['tipo']] = 'tipo'
            # Verdadeiro/Falso resposta
            for cand in ['resposta_correta', 'resposta_vf', 'correta_vf', 'vf']:
                if cand in norm_to_orig:
                    rename_map[norm_to_orig[cand]] = 'resposta_correta'
                    break
            # Alternativas por letra
            alt_letter_map = {
                'alternativa_a': 'alternativa_1',
                'alternativa_b': 'alternativa_2',
                'alternativa_c': 'alternativa_3',
                'alternativa_d': 'alternativa_4',
                'alternativa_e': 'alternativa_5',
            }
            for k, v in alt_letter_map.items():
                if k in norm_to_orig:
                    rename_map[norm_to_orig[k]] = v
            # Alternativas numéricas sem underscore (alternativa1)
            for i in range(1, 6):
                key = f'alternativa{i}'
                if key in norm_to_orig:
                    rename_map[norm_to_orig[key]] = f'alternativa_{i}'
            # Flags de correta por letra
            letter_correct_map = {
                'alternativa_a_correta': 'alternativa_1_correta',
                'alternativa_b_correta': 'alternativa_2_correta',
                'alternativa_c_correta': 'alternativa_3_correta',
                'alternativa_d_correta': 'alternativa_4_correta',
                'alternativa_e_correta': 'alternativa_5_correta',
            }
            for k, v in letter_correct_map.items():
                if k in norm_to_orig:
                    rename_map[norm_to_orig[k]] = v
            # Coluna única indicando qual alternativa é a correta
            for cand in ['alternativa_correta', 'correta', 'resposta_correta_alt']:
                if cand in norm_to_orig:
                    rename_map[norm_to_orig[cand]] = 'alternativa_correta'
                    break

            # Aplicar renomeações
            if rename_map:
                df = df.rename(columns=rename_map)
            
            # Validar colunas obrigatórias
            colunas_obrigatorias = ['pergunta', 'tipo']
            colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]
            
            if colunas_faltando:
                return {
                    'sucesso': False,
                    'erro': f'Colunas obrigatórias faltando: {", ".join(colunas_faltando)}'
                }
            
            importadas = 0
            erros = []
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        linha_num = index + 2  # +2 porque pandas começa em 0 e temos cabeçalho
                        
                        # Validar dados obrigatórios
                        if pd.isna(row['pergunta']) or not str(row['pergunta']).strip():
                            erros.append(f'Linha {linha_num}: Pergunta não pode estar vazia')
                            continue
                        
                        # Normalizar tipo e aceitar sinônimos
                        if pd.isna(row['tipo']):
                            erros.append(f'Linha {linha_num}: Tipo deve ser "multipla_escolha" ou "verdadeiro_falso"')
                            continue
                        tipo_raw = str(row['tipo']).strip()
                        tipo_norm = _norm(tipo_raw)
                        if tipo_norm in {
                            'multipla_escolha', 'multipla', 'multipla__escolha', 'múltipla_escolha', 'múltipla',
                            'multiple_choice', 'multiple__choice', 'mc'
                        }:
                            tipo = 'multipla_escolha'
                        elif tipo_norm in {
                            'verdadeiro_falso', 'verdadeiro__falso', 'vf', 'true_false', 'true__false', 'tf'
                        }:
                            tipo = 'verdadeiro_falso'
                        else:
                            erros.append(f'Linha {linha_num}: Tipo inválido "{tipo_raw}". Use "multipla_escolha" ou "verdadeiro_falso"')
                            continue
                        pergunta_texto = str(row['pergunta']).strip()
                        
                        # Criar pergunta
                        pergunta = Pergunta.objects.create(
                            quiz=quiz,
                            pergunta=pergunta_texto,
                            tipo=tipo
                        )
                        
                        # Processar baseado no tipo
                        if tipo == 'verdadeiro_falso':
                            # Para verdadeiro/falso, aceitar várias colunas e valores
                            valor_vf = None
                            for vf_col in ['resposta_correta', 'resposta_vf', 'correta_vf', 'vf']:
                                if vf_col in df.columns and not pd.isna(row.get(vf_col)):
                                    valor_vf = str(row.get(vf_col)).strip().lower()
                                    break
                            if valor_vf is None:
                                erros.append(f'Linha {linha_num}: Coluna de resposta obrigatória para V/F (ex.: "resposta_correta" ou "resposta_vf")')
                                pergunta.delete()
                                continue
                            if valor_vf in ['verdadeiro', 'true', '1', 'sim', 'v', 'yes', 's']:
                                pergunta.resposta_verdadeiro_falso = True
                            elif valor_vf in ['falso', 'false', '0', 'não', 'nao', 'f', 'no', 'n']:
                                pergunta.resposta_verdadeiro_falso = False
                            else:
                                erros.append(f'Linha {linha_num}: Resposta correta inválida para V/F')
                                pergunta.delete()
                                continue
                            pergunta.save()
                        
                        elif tipo == 'multipla_escolha':
                            # Para múltipla escolha, aceitar alternativas por número ou letra e coluna única de correta
                            alt_texts = []
                            alt_flags = []  # flags booleans por coluna alternativa_i_correta
                            for i in range(1, 6):
                                col_alt = f'alternativa_{i}'
                                col_flag = f'alternativa_{i}_correta'
                                if col_alt in df.columns and not pd.isna(row.get(col_alt)):
                                    texto = str(row.get(col_alt)).strip()
                                    if texto:
                                        alt_texts.append(texto)
                                        # flag de correta se existir
                                        flag_val = False
                                        if col_flag in df.columns and not pd.isna(row.get(col_flag)):
                                            v = str(row.get(col_flag)).strip().lower()
                                            flag_val = v in ['true', '1', 'sim', 'verdadeiro']
                                        alt_flags.append(flag_val)
                            alternativas_criadas = len(alt_texts)
                            
                            # Validar quantidade mínima
                            if alternativas_criadas < 2:
                                erros.append(f'Linha {linha_num}: Múltipla escolha precisa de pelo menos 2 alternativas')
                                pergunta.delete()
                                continue
                            
                            # Determinar alternativa correta
                            correta_idx = None
                            if any(alt_flags):
                                # Deve haver exatamente uma correta
                                idxs = [i for i, f in enumerate(alt_flags) if f]
                                if len(idxs) > 1:
                                    erros.append(f'Linha {linha_num}: Apenas uma alternativa pode ser correta')
                                    pergunta.delete()
                                    continue
                                correta_idx = idxs[0]
                            else:
                                # Fallback: coluna alternativa_correta com letra/numero/texto
                                if 'alternativa_correta' in df.columns and not pd.isna(row.get('alternativa_correta')):
                                    val = str(row.get('alternativa_correta')).strip().lower()
                                    # letra -> índice
                                    letter_to_idx = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
                                    if val in letter_to_idx:
                                        correta_idx = letter_to_idx[val]
                                    elif val in ['1', '2', '3', '4', '5']:
                                        correta_idx = int(val) - 1
                                    else:
                                        # tentar por texto
                                        try:
                                            correta_idx = [t.lower() for t in alt_texts].index(val)
                                        except ValueError:
                                            correta_idx = None
                                
                            if correta_idx is None or correta_idx >= alternativas_criadas:
                                erros.append(f'Linha {linha_num}: Múltipla escolha precisa de uma alternativa correta')
                                pergunta.delete()
                                continue
                            
                            # Criar alternativas
                            for i, texto in enumerate(alt_texts):
                                Alternativa.objects.create(
                                    pergunta=pergunta,
                                    texto=texto,
                                    correta=(i == correta_idx)
                                )
                        
                        importadas += 1
                        
                    except Exception as e:
                        erros.append(f'Linha {linha_num}: Erro ao processar - {str(e)}')
                        continue
            
            return {
                'sucesso': True,
                'importadas': importadas,
                'erros': erros
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao ler arquivo: {str(e)}'
            }


class DownloadTemplateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View para download do template da planilha"""
    login_url = 'account_login'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get(self, request, *args, **kwargs):
        # Criar template da planilha
        template_data = {
            'pergunta': [
                'Qual é a capital do Brasil?',
                'O Django é um framework Python?',
                'Quantos dias tem uma semana?'
            ],
            'tipo': [
                'multipla_escolha',
                'verdadeiro_falso',
                'multipla_escolha'
            ],
            'alternativa_1': [
                'São Paulo',
                '',
                '5'
            ],
            'alternativa_1_correta': [
                'false',
                '',
                'false'
            ],
            'alternativa_2': [
                'Rio de Janeiro',
                '',
                '6'
            ],
            'alternativa_2_correta': [
                'false',
                '',
                'false'
            ],
            'alternativa_3': [
                'Brasília',
                '',
                '7'
            ],
            'alternativa_3_correta': [
                'true',
                '',
                'true'
            ],
            'alternativa_4': [
                'Salvador',
                '',
                '8'
            ],
            'alternativa_4_correta': [
                'false',
                '',
                'false'
            ],
            'resposta_correta': [
                '',
                'verdadeiro',
                ''
            ]
        }
        
        df = pd.DataFrame(template_data)
        
        # Criar arquivo Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Template')
        
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="template_perguntas.xlsx"'
        
        return response
    