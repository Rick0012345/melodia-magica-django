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
from .models import Quiz, Pergunta, Alternativa, Pontuacao



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



    