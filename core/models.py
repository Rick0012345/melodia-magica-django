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
    # Campo simples para verdadeiro/falso: True = Verdadeiro é correto, False = Falso é correto
    resposta_verdadeiro_falso = models.BooleanField(
        null=True, 
        blank=True,
        help_text="Para questões Verdadeiro/Falso: marque se a resposta correta for 'Verdadeiro'"
    )

    def __str__(self):
        return self.pergunta
    
    def validar_resposta(self, resposta):
        """
        Valida a resposta do usuário para esta pergunta.
        
        Args:
            resposta (str): A resposta do usuário
            
        Returns:
            bool: True se a resposta estiver correta, False caso contrário
        """
        if self.tipo == 'multipla_escolha':
            # Para múltipla escolha, a resposta é o ID da alternativa
            try:
                alternativa = self.alternativas.get(id=int(resposta))  # type: ignore
                return alternativa.correta
            except (ValueError, Alternativa.DoesNotExist):  # type: ignore
                return False
                
        elif self.tipo == 'verdadeiro_falso':
            # Para verdadeiro/falso, usar o campo resposta_verdadeiro_falso
            if self.resposta_verdadeiro_falso is not None:
                # Usar o novo sistema simplificado
                if resposta.lower() == 'true':
                    return self.resposta_verdadeiro_falso is True
                elif resposta.lower() == 'false':
                    return self.resposta_verdadeiro_falso is False
                else:
                    return False
            else:
                # Fallback para o sistema antigo usando alternativas
                alternativa_correta = self.alternativas.filter(correta=True).first()  # type: ignore
                if not alternativa_correta:
                    return False
                
                if resposta.lower() == 'true':
                    return alternativa_correta.texto.lower() == 'verdadeiro'
                elif resposta.lower() == 'false':
                    return alternativa_correta.texto.lower() == 'falso'
                else:
                    return False
                
        else:
            # Para outros tipos de pergunta, implementar conforme necessário
            return False
    
    def get_alternativa_correta(self):
        """Retorna a alternativa correta desta pergunta"""
        return self.alternativas.filter(correta=True).first()  # type: ignore
    
    def has_alternativa_correta(self):
        """Verifica se a pergunta tem uma alternativa correta definida"""
        if self.tipo == 'verdadeiro_falso':
            return self.resposta_verdadeiro_falso is not None
        return self.alternativas.filter(correta=True).exists()  # type: ignore
    
    def total_alternativas(self):
        """Retorna o número total de alternativas desta pergunta"""
        return self.alternativas.count()  # type: ignore
    
    def is_questao_valida(self):
        """
        Verifica se a questão está válida:
        - Múltipla escolha: deve ter pelo menos 2 alternativas e exatamente 1 correta
        - Verdadeiro/Falso: deve ter resposta_verdadeiro_falso definida
        """
        if self.tipo == 'multipla_escolha':
            return (self.total_alternativas() >= 2 and 
                    self.alternativas.filter(correta=True).count() == 1)  # type: ignore
        elif self.tipo == 'verdadeiro_falso':
            return self.resposta_verdadeiro_falso is not None
        else:
            return True
    
    def get_resposta_correta_display(self):
        """Retorna a resposta correta em formato legível"""
        if self.tipo == 'verdadeiro_falso':
            if self.resposta_verdadeiro_falso is not None:
                return "Verdadeiro" if self.resposta_verdadeiro_falso else "Falso"
            else:
                # Fallback para sistema antigo
                alternativa_correta = self.get_alternativa_correta()
                return alternativa_correta.texto if alternativa_correta else "Não definido"
        elif self.tipo == 'multipla_escolha':
            alternativa_correta = self.get_alternativa_correta()
            return alternativa_correta.texto if alternativa_correta else "Não definido"
        return "Não definido"

class Alternativa(models.Model):
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE, related_name='alternativas')
    texto = models.CharField(max_length=100)
    correta = models.BooleanField(default=False)  # type: ignore

    def __str__(self):
        return self.texto

    class Meta:
        verbose_name = "Alternativa"
        verbose_name_plural = "Alternativas"

class Pontuacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    pontuacao = models.IntegerField()
    data_pontuacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'quiz')
        verbose_name = "Pontuação"
        verbose_name_plural = "Pontuações"

    def __str__(self):
        return f"{self.usuario.username} - {self.quiz.titulo}: {self.pontuacao}"  # type: ignore
