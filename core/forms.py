from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Quiz, Pergunta, Alternativa

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['titulo', 'descricao', 'nivel_dificuldade']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do quiz'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva o quiz'
            }),
            'nivel_dificuldade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'placeholder': 'Nível de 1 a 10'
            })
        }

class PerguntaForm(forms.ModelForm):
    class Meta:
        model = Pergunta
        fields = ['pergunta', 'quiz', 'tipo', 'resposta_verdadeiro_falso']
        widgets = {
            'pergunta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a pergunta'
            }),
            'quiz': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_tipo'
            }),
            'resposta_verdadeiro_falso': forms.Select(
                choices=[(None, '--- Selecione ---'), (True, 'Verdadeiro'), (False, 'Falso')],
                attrs={
                    'class': 'form-control',
                    'id': 'id_resposta_vf'
                }
            )
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar o campo quiz opcional se estivermos editando
        if self.instance.pk:
            self.fields['quiz'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        resposta_verdadeiro_falso = cleaned_data.get('resposta_verdadeiro_falso')
        
        # Validar questões de verdadeiro/falso
        if tipo == 'verdadeiro_falso':
            if resposta_verdadeiro_falso is None:
                raise ValidationError({
                    'resposta_verdadeiro_falso': 'Para questões de Verdadeiro/Falso, você deve definir se a resposta correta é Verdadeiro ou Falso.'
                })
        
        # Limpar campo resposta_verdadeiro_falso para outros tipos
        elif tipo != 'verdadeiro_falso':
            cleaned_data['resposta_verdadeiro_falso'] = None
            
        return cleaned_data

class AlternativaForm(forms.ModelForm):
    class Meta:
        model = Alternativa
        fields = ['texto', 'correta']
        widgets = {
            'texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a alternativa'
            }),
            'correta': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

# Formset para alternativas
AlternativaFormSet = inlineformset_factory(
    Pergunta, 
    Alternativa, 
    form=AlternativaForm,
    extra=4,  # 4 alternativas por padrão
    max_num=6,  # Máximo 6 alternativas
    min_num=2,  # Mínimo 2 alternativas para múltipla escolha
    can_delete=True,
    validate_min=False,  # Validação customizada
    validate_max=True
)

class PerguntaComAlternativasForm(forms.Form):
    """Form combinado para pergunta + alternativas"""
    
    def __init__(self, *args, **kwargs):
        self.pergunta_instance = kwargs.pop('pergunta_instance', None)
        self.quiz = kwargs.pop('quiz', None)
        super().__init__(*args, **kwargs)
        
        # Adicionar campos da pergunta
        self.pergunta_form = PerguntaForm(
            *args, 
            instance=self.pergunta_instance,
            prefix='pergunta',
            **kwargs
        )
        
        # Se temos um quiz específico, definir como padrão
        if self.quiz:
            self.pergunta_form.fields['quiz'].initial = self.quiz.id
            self.pergunta_form.fields['quiz'].widget = forms.HiddenInput()
            self.pergunta_form.fields['quiz'].required = True
        
        # Adicionar formset de alternativas
        self.alternativa_formset = AlternativaFormSet(
            *args,
            instance=self.pergunta_instance,
            prefix='alternativas',
            **kwargs
        )
    
    def is_valid(self):
        pergunta_valid = self.pergunta_form.is_valid()
        alternativas_valid = True
        
        # Validar alternativas apenas para múltipla escolha
        if self.pergunta_form.is_valid():
            tipo = self.pergunta_form.cleaned_data.get('tipo')
            if tipo == 'multipla_escolha':
                alternativas_valid = self.alternativa_formset.is_valid()
                
                # Validação customizada: pelo menos uma alternativa correta
                if alternativas_valid:
                    alternativas_corretas = 0
                    alternativas_preenchidas = 0
                    
                    for form in self.alternativa_formset.forms:
                        if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                            alternativas_preenchidas += 1
                            if form.cleaned_data.get('correta', False):
                                alternativas_corretas += 1
                    
                    if alternativas_preenchidas < 2:
                        self.alternativa_formset.non_form_errors().append(
                            'Questões de múltipla escolha devem ter pelo menos 2 alternativas.'
                        )
                        alternativas_valid = False
                    
                    if alternativas_corretas != 1:
                        self.alternativa_formset.non_form_errors().append(
                            'Questões de múltipla escolha devem ter exatamente 1 alternativa correta.'
                        )
                        alternativas_valid = False
        
        return pergunta_valid and alternativas_valid
    
    def save(self, commit=True):
        print(f"DEBUG SAVE: Iniciando save do formulário")
        print(f"DEBUG SAVE: pergunta_form.cleaned_data = {self.pergunta_form.cleaned_data}")
        
        # Salvar pergunta
        pergunta = self.pergunta_form.save(commit=commit)
        print(f"DEBUG SAVE: Pergunta salva com ID: {pergunta.id}, Quiz: {pergunta.quiz}")
        
        # Salvar alternativas apenas para múltipla escolha
        if pergunta.tipo == 'multipla_escolha':
            print(f"DEBUG SAVE: Salvando alternativas para múltipla escolha")
            self.alternativa_formset.instance = pergunta
            alternativas = self.alternativa_formset.save(commit=commit)
            print(f"DEBUG SAVE: {len(alternativas)} alternativas salvas")
        else:
            # Remover alternativas existentes para outros tipos
            if pergunta.pk:
                pergunta.alternativas.all().delete()
        
        return pergunta