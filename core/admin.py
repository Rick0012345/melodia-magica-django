from django.contrib import admin
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Quiz, Pergunta, Alternativa, Pontuacao

class PerguntaForm(ModelForm):
    """Form customizado para Pergunta com validação adequada"""
    
    class Meta:
        model = Pergunta
        fields = ['pergunta', 'quiz', 'tipo', 'resposta_verdadeiro_falso']
        
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

class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 2
    fields = ('texto', 'correta')
    
    def get_extra(self, request, obj=None, **kwargs):
        """Definir quantas alternativas extras mostrar baseado no tipo"""
        if obj and obj.tipo == 'multipla_escolha':
            return 4
        return 0
    
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
    list_display = ('titulo', 'nivel_dificuldade', 'data_criacao', 'total_perguntas')
    list_filter = ('nivel_dificuldade',)
    search_fields = ('titulo', 'descricao')
    inlines = [PerguntaInline]
    
    def total_perguntas(self, obj):
        """Mostrar total de perguntas do quiz"""
        return obj.perguntas.count()
    total_perguntas.short_description = "Total de Perguntas"

@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    form = PerguntaForm
    list_display = ('pergunta', 'quiz', 'tipo', 'resposta_correta_display', 'status_questao')
    list_filter = ('tipo', 'quiz')
    search_fields = ('pergunta',)
    
    class Media:
        css = {
            'all': ('admin/css/pergunta-admin.css',)
        }
        js = ('admin/js/pergunta-admin.js',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('pergunta', 'quiz', 'tipo')
        }),
        ('Resposta Correta (Verdadeiro/Falso)', {
            'fields': ('resposta_verdadeiro_falso',),
            'description': 'Para questões de Verdadeiro/Falso: marque a caixa se a resposta correta for "Verdadeiro", ou deixe desmarcada se for "Falso". Este campo é ignorado para outros tipos de questão.',
            'classes': ('collapse',)
        }),
    )
    
    def resposta_correta_display(self, obj):
        """Mostrar resposta correta em formato legível"""
        return obj.get_resposta_correta_display()
    resposta_correta_display.short_description = "Resposta Correta"
    
    def status_questao(self, obj):
        """Mostrar status da questão (válida ou não)"""
        if obj.is_questao_valida():
            return "✅ Válida"
        else:
            return "❌ Inválida"
    status_questao.short_description = "Status"
    
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
    list_display = ('texto', 'pergunta', 'tipo_pergunta', 'correta')
    list_filter = ('correta', 'pergunta__quiz', 'pergunta__tipo')
    search_fields = ('texto', 'pergunta__pergunta')
    
    def tipo_pergunta(self, obj):
        """Mostrar tipo da pergunta"""
        return obj.pergunta.get_tipo_display()
    tipo_pergunta.short_description = "Tipo"
    
    def get_queryset(self, request):
        """Mostrar apenas alternativas de questões de múltipla escolha"""
        qs = super().get_queryset(request)
        return qs.filter(pergunta__tipo='multipla_escolha')

@admin.register(Pontuacao)
class PontuacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'quiz', 'pontuacao', 'data_pontuacao')
    list_filter = ('quiz', 'data_pontuacao')
    search_fields = ('usuario__username', 'quiz__titulo')
    readonly_fields = ('data_pontuacao',)
    
    def has_add_permission(self, request):
        """Não permitir adicionar pontuações manualmente"""
        return False
