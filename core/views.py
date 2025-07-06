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
        
        # Verifica se o usuário quer reiniciar o quiz
        reiniciar = self.request.GET.get('reiniciar') == 'true'
        if reiniciar:
            # Limpa toda a sessão do quiz
            self.request.session.pop('pontuacao', None)
            self.request.session.pop('acertos', None)
            self.request.session.pop('erros', None)
            self.request.session.pop('pergunta_atual_id', None)
            self.request.session.pop('quiz_finalizado', None)
        
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
        
        # Pega todas as perguntas ordenadas por ID
        todas_perguntas = list(quiz.perguntas.order_by('id').values_list('id', flat=True))
        
        if pergunta_atual_id:
            # Encontra a posição da pergunta atual na lista
            try:
                posicao_atual = todas_perguntas.index(int(pergunta_atual_id))
                # Progresso baseado na posição (0-indexed)
                progresso = ((posicao_atual + 1) / total_perguntas) * 100
            except ValueError:
                progresso = 0
        else:
            # Se não há pergunta atual, é a primeira pergunta
            progresso = (1 / total_perguntas) * 100 if total_perguntas > 0 else 0
        
        # Garante que o progresso esteja entre 0 e 100
        progresso = max(0, min(100, progresso))
        
        # Debug: Adiciona informações de debug ao contexto
        context['debug_info'] = {
            'total_perguntas': total_perguntas,
            'pergunta_atual_id': pergunta_atual_id,
            'todas_perguntas_ids': todas_perguntas,
            'posicao_atual': todas_perguntas.index(int(pergunta_atual_id)) if pergunta_atual_id else 0,
            'progresso_calculado': progresso
        }
        
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
            
            request.session['quiz_finalizado'] = True
            
            return redirect('game_page', quiz_id=quiz_id)

    def get(self, request, *args, **kwargs):
        if request.session.get('quiz_finalizado', False) and request.GET.get('voltar') == 'true':
            request.session.pop('pontuacao', None)
            request.session.pop('acertos', None)
            request.session.pop('erros', None)
            request.session.pop('pergunta_atual_id', None)
            request.session.pop('quiz_finalizado', None)
            
            return redirect('niveis')
        
        return super().get(request, *args, **kwargs)
    