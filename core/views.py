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
from .models import Quiz, Pergunta, Alternativa



class HomeView(TemplateView):
    template_name = "core/index.html"

class ServicosView(TemplateView):
    template_name = "core/servicos.html"

class ContatoView(TemplateView):
    template_name = "core/contato.html"

class LoginView(TemplateView):
    template_name = "core/login.html"

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
        
        # Pega a primeira pergunta do quiz
        pergunta = quiz.perguntas.first()
        
        context['quiz'] = quiz
        context['pergunta'] = pergunta
        return context

    def post(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id)
        resposta = request.POST.get('resposta')
        
        # Aqui você pode adicionar a lógica para verificar a resposta
        # e atualizar a pontuação do usuário
        
        # Pega a próxima pergunta
        pergunta_atual_id = request.POST.get('pergunta_atual_id')
        proxima_pergunta = quiz.perguntas.filter(id__gt=pergunta_atual_id).first()
        
        if proxima_pergunta:
            return redirect('game_page', quiz_id=quiz_id)
        else:
            # Quiz finalizado
            return redirect('niveis')

class CadastrarQuestoesView(TemplateView):
    template_name = "core/cadastrar_questoes.html"

    def post(self, request, *args, **kwargs):
        pergunta_texto = request.POST.get('pergunta')
        tipo = request.POST.get('tipo')
        quiz_id = request.POST.get('quiz_id')
        
        if not quiz_id:
            messages.error(request, 'É necessário selecionar um quiz!')
            return redirect('cadastrar_questoes')
        
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Criar a pergunta
        pergunta = Pergunta.objects.create(
            pergunta=pergunta_texto,
            tipo=tipo,
            quiz=quiz
        )
        
        # Processar alternativas para questões de múltipla escolha
        if tipo == 'multipla_escolha':
            alternativas = request.POST.getlist('alternativa')
            corretas = request.POST.getlist('correta')
            
            for i, texto in enumerate(alternativas):
                if texto.strip():  # Só cria se houver texto
                    Alternativa.objects.create(
                        pergunta=pergunta,
                        texto=texto,
                        correta=str(i) in corretas
                    )
        elif tipo == 'verdadeiro_falso':
            resposta_correta = request.POST.get('resposta_vf')
            if resposta_correta:
                # Criar alternativa Verdadeiro
                Alternativa.objects.create(
                    pergunta=pergunta,
                    texto='Verdadeiro',
                    correta=resposta_correta == 'true'
                )
                # Criar alternativa Falso
                Alternativa.objects.create(
                    pergunta=pergunta,
                    texto='Falso',
                    correta=resposta_correta == 'false'
                )
        
        messages.success(request, 'Questão cadastrada com sucesso!')
        return redirect('cadastrar_questoes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['perguntas'] = Pergunta.objects.all().order_by('-id')
        context['quizzes'] = Quiz.objects.all()
        return context


def cadastrar_quiz(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        nivel_dificuldade = request.POST.get('nivel_dificuldade')
        
        quiz = Quiz.objects.create(
            titulo=titulo,
            descricao=descricao,
            nivel_dificuldade=nivel_dificuldade
        )
        messages.success(request, 'Quiz criado com sucesso!')
        return redirect('cadastrar_pergunta', quiz_id=quiz.id)
    
    return render(request, 'core/cadastrar_quiz.html')


def cadastrar_pergunta(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        pergunta_texto = request.POST.get('pergunta')
        tipo = request.POST.get('tipo')
        
        pergunta = Pergunta.objects.create(
            pergunta=pergunta_texto,
            quiz=quiz,
            tipo=tipo
        )
        
        # Processar alternativas para questões de múltipla escolha
        if tipo == 'multipla_escolha':
            alternativas = request.POST.getlist('alternativa')
            corretas = request.POST.getlist('correta')
            
            for i, texto in enumerate(alternativas):
                if texto.strip():  # Só cria se houver texto
                    Alternativa.objects.create(
                        pergunta=pergunta,
                        texto=texto,
                        correta=str(i) in corretas
                    )
        
        messages.success(request, 'Pergunta cadastrada com sucesso!')
        return redirect('cadastrar_pergunta', quiz_id=quiz.id)
    
    perguntas = quiz.perguntas.all()
    return render(request, 'core/cadastrar_pergunta.html', {
        'quiz': quiz,
        'perguntas': perguntas
    })


def editar_pergunta(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    
    if request.method == 'POST':
        pergunta.pergunta = request.POST.get('pergunta')
        pergunta.tipo = request.POST.get('tipo')
        pergunta.save()
        
        # Atualizar alternativas se for múltipla escolha
        if pergunta.tipo == 'multipla_escolha':
            pergunta.alternativas.all().delete()  # Remove alternativas antigas
            alternativas = request.POST.getlist('alternativa')
            corretas = request.POST.getlist('correta')
            
            for i, texto in enumerate(alternativas):
                if texto.strip():
                    Alternativa.objects.create(
                        pergunta=pergunta,
                        texto=texto,
                        correta=str(i) in corretas
                    )
        
        messages.success(request, 'Pergunta atualizada com sucesso!')
        return redirect('cadastrar_pergunta', quiz_id=pergunta.quiz.id)
    
    return render(request, 'core/editar_pergunta.html', {
        'pergunta': pergunta
    })


def excluir_pergunta(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    quiz_id = pergunta.quiz.id
    pergunta.delete()
    messages.success(request, 'Pergunta excluída com sucesso!')
    return redirect('cadastrar_pergunta', quiz_id=quiz_id)



    