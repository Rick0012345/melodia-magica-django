from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    nivel_dificuldade = models.IntegerField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Pergunta(models.Model):
    TIPO_CHOICES = [
        ('multipla_escolha', 'Múltipla Escolha'),
        ('verdadeiro_falso', 'Verdadeiro/Falso'),
        ('texto_livre', 'Texto Livre'),
    ]
    
    pergunta = models.CharField(max_length=255)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='perguntas')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return self.pergunta

class Alternativa(models.Model):
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE, related_name='alternativas')
    texto = models.CharField(max_length=100)
    correta = models.BooleanField(default=False)

    def __str__(self):
        return self.texto

class Pontuacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    pontuacao = models.IntegerField()
    data_pontuacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'quiz')

    def __str__(self):
        return f"{self.usuario.username} - {self.quiz.titulo}: {self.pontuacao}"
