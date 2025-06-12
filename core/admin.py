from django.contrib import admin
from .models import Quiz, Pergunta, Alternativa

class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 4

class PerguntaInline(admin.TabularInline):
    model = Pergunta
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'nivel_dificuldade', 'data_criacao')
    list_filter = ('nivel_dificuldade',)
    search_fields = ('titulo', 'descricao')
    inlines = [PerguntaInline]

@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('pergunta', 'quiz', 'tipo')
    list_filter = ('tipo', 'quiz')
    search_fields = ('pergunta',)
    inlines = [AlternativaInline]

@admin.register(Alternativa)
class AlternativaAdmin(admin.ModelAdmin):
    list_display = ('texto', 'pergunta', 'correta')
    list_filter = ('correta', 'pergunta__quiz')
    search_fields = ('texto',)
