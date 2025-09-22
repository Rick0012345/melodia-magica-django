from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import ValidationError
from .models import Quiz, Pergunta, Alternativa, Pontuacao

# Filtros customizados
class TipoFilter(SimpleListFilter):
    title = 'Tipo de Pergunta'
    parameter_name = 'tipo'
    
    def lookups(self, request, model_admin):
        return Pergunta.TIPO_CHOICES
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tipo=self.value())
        return queryset

# Formulário customizado para perguntas
class PerguntaForm(forms.ModelForm):
    """Form customizado para Pergunta com validação adequada"""
    
    class Meta:
        model = Pergunta
        fields = '__all__'
        widgets = {
            'pergunta': forms.Textarea(attrs={
                'rows': 4, 
                'cols': 80,
                'class': 'form-control',
                'placeholder': 'Digite o texto da pergunta aqui...'
            }),
            'feedback_validacao': forms.Textarea(attrs={
                'rows': 3,
                'cols': 80,
                'class': 'form-control',
                'placeholder': 'Feedback sobre a validação da pergunta...'
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        resposta_verdadeiro_falso = cleaned_data.get('resposta_verdadeiro_falso')
        
        # Validar questões de verdadeiro/falso
        if tipo == 'verdadeiro_falso':
            if resposta_verdadeiro_falso is None:
                raise ValidationError(
                    'Para questões de Verdadeiro/Falso, você deve definir se a resposta correta é Verdadeiro ou Falso.'
                )
        
        # Limpar campo resposta_verdadeiro_falso para outros tipos
        elif tipo != 'verdadeiro_falso':
            cleaned_data['resposta_verdadeiro_falso'] = None
            
        return cleaned_data

# Formulário customizado para alternativas
class AlternativaForm(forms.ModelForm):
    class Meta:
        model = Alternativa
        fields = '__all__'
        widgets = {
            'texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o texto da alternativa...',
                'style': 'width: 100%;'
            }),
        }
    
    def clean_texto(self):
        texto = self.cleaned_data.get('texto')
        if texto and len(texto.strip()) < 2:
            raise forms.ValidationError('O texto da alternativa deve ter pelo menos 2 caracteres.')
        return texto

# Inline melhorado para alternativas
class AlternativaInline(admin.TabularInline):
    model = Alternativa
    form = AlternativaForm
    extra = 4
    max_num = 6
    min_num = 2
    fields = ['texto', 'correta']
    ordering = ['id']
    
    # Media removida para otimização
    
    def get_extra(self, request, obj=None, **kwargs):
        """Ajusta o número de formulários extras baseado no tipo da pergunta"""
        if obj and obj.tipo == 'verdadeiro_falso':
            return 0
        return self.extra
    
    def get_min_num(self, request, obj=None, **kwargs):
        """Define o número mínimo de alternativas baseado no tipo"""
        if obj and obj.tipo == 'verdadeiro_falso':
            return 0
        return self.min_num
    
    def get_max_num(self, request, obj=None, **kwargs):
        """Define o número máximo de alternativas baseado no tipo"""
        if obj and obj.tipo == 'verdadeiro_falso':
            return 0
        return self.max_num
    
    def get_formset(self, request, obj=None, **kwargs):
        """Personalizar formset para questões de múltipla escolha"""
        formset = super().get_formset(request, obj, **kwargs)
        
        # Adicionar validação customizada apenas para múltipla escolha
        if obj and obj.tipo == 'multipla_escolha':
            original_clean = formset.clean
            
            def clean(self):
                # Executar validação padrão
                if hasattr(original_clean, '__call__'):
                    original_clean(self)
                
                # Verificar se há erros
                if any(self.errors):
                    return
                
                corretas = 0
                total_alternativas = 0
                
                for form in self.forms:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        total_alternativas += 1
                        if form.cleaned_data.get('correta', False):
                            corretas += 1
                
                # Validação específica para múltipla escolha
                if corretas == 0:
                    raise ValidationError(
                        'Questões de múltipla escolha devem ter exatamente 1 alternativa correta.'
                    )
                elif corretas > 1:
                    raise ValidationError(
                        'Questões de múltipla escolha devem ter apenas 1 alternativa correta. '
                        f'Você marcou {corretas} alternativas como corretas.'
                    )
                
                if total_alternativas < 2:
                    raise ValidationError(
                        'Questões de múltipla escolha devem ter pelo menos 2 alternativas.'
                    )
            
            formset.clean = clean
        
        return formset

class PerguntaInline(admin.TabularInline):
    model = Pergunta
    extra = 1
    fields = ('pergunta', 'tipo', 'resposta_verdadeiro_falso')
    form = PerguntaForm

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'nivel_dificuldade', 'get_num_perguntas', 
        'get_status_badge', 'data_criacao'
    ]
    list_filter = ['nivel_dificuldade', 'data_criacao']
    search_fields = ['titulo', 'descricao']
    ordering = ['-data_criacao']
    list_per_page = 20
    date_hierarchy = 'data_criacao'
    inlines = [PerguntaInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'nivel_dificuldade')
        }),
        ('Metadados', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['data_criacao']
    
    def get_num_perguntas(self, obj):
        count = obj.perguntas.count()
        if count == 0:
            return format_html('<span style="color: #dc3545;">0</span>')
        return count
    get_num_perguntas.short_description = 'Total Perguntas'
    get_num_perguntas.admin_order_field = 'perguntas__count'
    
    def get_status_badge(self, obj):
        total = obj.perguntas.count()
        
        if total == 0:
            return format_html('<span class="badge" style="background-color: #6c757d;">Vazio</span>')
        else:
            return format_html('<span class="badge" style="background-color: #28a745;">Ativo</span>')
    get_status_badge.short_description = 'Status'
    
    actions = ['duplicate_quiz']
    
    def duplicate_quiz(self, request, queryset):
        for quiz in queryset:
            # Criar cópia do quiz
            new_quiz = Quiz.objects.create(
                titulo=f"{quiz.titulo} (Cópia)",
                descricao=quiz.descricao,
                nivel_dificuldade=quiz.nivel_dificuldade
            )
            
            # Copiar perguntas
            for pergunta in quiz.perguntas.all():
                new_pergunta = Pergunta.objects.create(
                    quiz=new_quiz,
                    pergunta=pergunta.pergunta,
                    tipo=pergunta.tipo,
                    resposta_verdadeiro_falso=pergunta.resposta_verdadeiro_falso,
                    # Pergunta duplicada
                )
                
                # Copiar alternativas
                for alternativa in pergunta.alternativas.all():
                    Alternativa.objects.create(
                        pergunta=new_pergunta,
                        texto=alternativa.texto,
                        correta=alternativa.correta
                    )
        
        self.message_user(request, f'{queryset.count()} quiz(es) duplicado(s) com sucesso.')
    duplicate_quiz.short_description = 'Duplicar quizzes selecionados'
    
    def total_perguntas(self, obj):
        """Mostrar total de perguntas do quiz"""
        return obj.perguntas.count()
    total_perguntas.short_description = "Total de Perguntas"

@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    form = PerguntaForm
    list_display = [
        'pergunta_resumo', 'quiz', 'tipo', 
        'get_alternativas_count', 'get_resposta_correta'
    ]
    list_filter = [TipoFilter, 'quiz']
    search_fields = ['pergunta', 'quiz__titulo']
    ordering = ['id']
    inlines = [AlternativaInline]
    list_per_page = 25
    
    # Media removida para otimização
    
    fieldsets = (
        ('Pergunta', {
            'fields': ('quiz', 'pergunta', 'tipo')
        }),
        ('Resposta (apenas para Verdadeiro/Falso)', {
            'fields': ('resposta_verdadeiro_falso',),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'duplicar_perguntas'
    ]
    
    def pergunta_resumo(self, obj):
        texto = obj.pergunta[:60] + '...' if len(obj.pergunta) > 60 else obj.pergunta
        return format_html('<span title="{}">{}</span>', obj.pergunta, texto)
    pergunta_resumo.short_description = 'Pergunta'
    

    
    def get_alternativas_count(self, obj):
        if obj.tipo == 'verdadeiro_falso':
            return format_html('<span style="color: #6c757d;">-</span>')
        
        count = obj.alternativas.count()
        corretas = obj.alternativas.filter(correta=True).count()
        
        if count == 0:
            return format_html('<span style="color: #dc3545;">0</span>')
        elif corretas == 0:
            return format_html(
                '<span style="color: #dc3545;" title="Nenhuma alternativa marcada como correta">{} ⚠️</span>',
                count
            )
        elif corretas > 1:
            return format_html(
                '<span style="color: #ffc107;" title="Múltiplas alternativas corretas">{} ⚠️</span>',
                count
            )
        else:
            return format_html('<span style="color: #28a745;">{}</span>', count)
    get_alternativas_count.short_description = 'Alternativas'
    
    def get_resposta_correta(self, obj):
        if obj.tipo == 'verdadeiro_falso':
            if obj.resposta_verdadeiro_falso is None:
                return format_html('<span style="color: #dc3545;">Não definida</span>')
            return format_html(
                '<span style="color: #28a745;">{}</span>',
                'Verdadeiro' if obj.resposta_verdadeiro_falso else 'Falso'
            )
        else:
            corretas = obj.alternativas.filter(correta=True)
            if not corretas.exists():
                return format_html('<span style="color: #dc3545;">Nenhuma</span>')
            elif corretas.count() > 1:
                return format_html('<span style="color: #ffc107;">Múltiplas</span>')
            else:
                texto = corretas.first().texto
                resumo = texto[:30] + '...' if len(texto) > 30 else texto
                return format_html('<span title="{}">{}</span>', texto, resumo)
    get_resposta_correta.short_description = 'Resposta Correta'
    
    # Ações em lote
    def duplicar_perguntas(self, request, queryset):
        for pergunta in queryset:
            new_pergunta = Pergunta.objects.create(
                quiz=pergunta.quiz,
                pergunta=f"{pergunta.pergunta} (Cópia)",
                tipo=pergunta.tipo,
                resposta_verdadeiro_falso=pergunta.resposta_verdadeiro_falso
            )
            
            # Copiar alternativas
            for alternativa in pergunta.alternativas.all():
                Alternativa.objects.create(
                    pergunta=new_pergunta,
                    texto=alternativa.texto,
                    correta=alternativa.correta
                )
        
        self.message_user(request, f'{queryset.count()} pergunta(s) duplicada(s) com sucesso.')
    duplicar_perguntas.short_description = 'Duplicar perguntas selecionadas'
    
    def get_inlines(self, request, obj):
        """Mostrar inline de alternativas apenas para questões de múltipla escolha"""
        if obj and obj.tipo == 'multipla_escolha':
            return [AlternativaInline]
        return []
    
    def save_model(self, request, obj, form, change):
        """Salvar modelo com limpeza de dados"""
        super().save_model(request, obj, form, change)
        
        # Para questões de verdadeiro/falso, remover alternativas antigas se existirem
        if obj.tipo == 'verdadeiro_falso':
            obj.alternativas.all().delete()

@admin.register(Alternativa)
class AlternativaAdmin(admin.ModelAdmin):
    list_display = [
        'texto_resumo', 'pergunta_resumo', 'quiz_info', 'correta_badge', 
        'get_pergunta_status'
    ]
    list_filter = ['correta', 'pergunta__quiz', 'pergunta__tipo']
    search_fields = ['texto', 'pergunta__pergunta', 'pergunta__quiz__titulo']
    ordering = ['pergunta', 'id']
    list_per_page = 30
    
    fieldsets = (
        ('Alternativa', {
            'fields': ('pergunta', 'texto', 'correta')
        }),
    )
    
    def texto_resumo(self, obj):
        texto = obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
        return format_html('<span title="{}">{}</span>', obj.texto, texto)
    texto_resumo.short_description = 'Texto'
    
    def pergunta_resumo(self, obj):
        pergunta = obj.pergunta.pergunta[:40] + '...' if len(obj.pergunta.pergunta) > 40 else obj.pergunta.pergunta
        return format_html('<span title="{}">{}</span>', obj.pergunta.pergunta, pergunta)
    pergunta_resumo.short_description = 'Pergunta'
    
    def quiz_info(self, obj):
        return format_html(
            '<a href="{}" title="{}">{}</a>',
            reverse('admin:core_quiz_change', args=[obj.pergunta.quiz.id]),
            obj.pergunta.quiz.titulo,
            obj.pergunta.quiz.titulo[:20] + '...' if len(obj.pergunta.quiz.titulo) > 20 else obj.pergunta.quiz.titulo
        )
    quiz_info.short_description = 'Quiz'
    
    def correta_badge(self, obj):
        if obj.correta:
            return format_html('<span style="color: #28a745; font-weight: bold;">✅ Correta</span>')
        else:
            return format_html('<span style="color: #6c757d;">❌ Incorreta</span>')
    correta_badge.short_description = 'Status'
    correta_badge.admin_order_field = 'correta'
    
    def get_pergunta_status(self, obj):
        return format_html('<span style="color: #28a745;">✅</span>')
    get_pergunta_status.short_description = 'Status'
    
    def get_queryset(self, request):
        """Mostrar apenas alternativas de questões de múltipla escolha"""
        qs = super().get_queryset(request)
        return qs.filter(pergunta__tipo='multipla_escolha')

@admin.register(Pontuacao)
class PontuacaoAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'quiz_info', 'pontuacao_badge', 'percentual', 
        'data_pontuacao'
    ]
    list_filter = ['quiz', 'data_pontuacao']
    search_fields = ['usuario__username', 'quiz__titulo']
    ordering = ['-data_pontuacao']
    list_per_page = 25
    date_hierarchy = 'data_pontuacao'
    
    fieldsets = (
        ('Resultado', {
            'fields': ('usuario', 'quiz', 'pontuacao')
        }),
        ('Detalhes', {
            'fields': ('data_pontuacao',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['data_pontuacao']
    
    def quiz_info(self, obj):
        total_perguntas = obj.quiz.perguntas.count()
        return format_html(
            '<a href="{}" title="{}">{}</a><br><small>{} perguntas</small>',
            reverse('admin:core_quiz_change', args=[obj.quiz.id]),
            obj.quiz.titulo,
            obj.quiz.titulo[:25] + '...' if len(obj.quiz.titulo) > 25 else obj.quiz.titulo,
            total_perguntas
        )
    quiz_info.short_description = 'Quiz'
    
    def pontuacao_badge(self, obj):
        total_perguntas = obj.quiz.perguntas.count()
        if total_perguntas == 0:
            return format_html('<span style="color: #6c757d;">-</span>')
        
        percentual = (obj.pontuacao / total_perguntas) * 100
        
        if percentual >= 80:
            color = '#28a745'
            icon = '🏆'
        elif percentual >= 60:
            color = '#ffc107'
            icon = '👍'
        else:
            color = '#dc3545'
            icon = '📚'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}/{}</span>',
            color, icon, obj.pontuacao, total_perguntas
        )
    pontuacao_badge.short_description = 'Pontuação'
    pontuacao_badge.admin_order_field = 'pontuacao'
    
    def percentual(self, obj):
        total_perguntas = obj.quiz.perguntas.count()
        if total_perguntas == 0:
            return format_html('<span style="color: #6c757d;">-</span>')
        
        percentual = (obj.pontuacao / total_perguntas) * 100
        color = '#28a745' if percentual >= 80 else '#ffc107' if percentual >= 60 else '#dc3545'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, percentual
        )
    percentual.short_description = 'Percentual'
    
    # Funcionalidades de tempo e exportação removidas para otimização
    
    def has_add_permission(self, request):
        """Não permitir adicionar pontuações manualmente"""
        return False
