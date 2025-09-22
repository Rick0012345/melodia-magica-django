from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import uuid
from .models import ChatMessage

def get_chatbot_response(message):
    """Função para gerar respostas do chatbot baseadas nas regras e informações do jogo"""
    message = message.lower().strip()
    
    # Palavras-chave para regras
    regras_keywords = ['regra', 'regras', 'como jogar', 'como funciona', 'pontuação', 'ponto', 'pontos']
    
    # Palavras-chave para informações sobre o jogo
    sobre_keywords = ['sobre', 'melodia mágica', 'quiz', 'jogo', 'música', 'instrumento', 'instrumentos']
    
    # Palavras-chave para saudações
    saudacao_keywords = ['oi', 'olá', 'hello', 'hi', 'bom dia', 'boa tarde', 'boa noite']
    
    # Palavras-chave para ajuda
    ajuda_keywords = ['ajuda', 'help', 'socorro', 'não entendo', 'confuso']
    
    if any(keyword in message for keyword in saudacao_keywords):
        return "Olá! 👋 Bem-vindo ao Melodia Mágica! Sou seu assistente virtual. Posso te ajudar com informações sobre as regras do jogo e sobre o projeto. O que você gostaria de saber?"
    
    elif any(keyword in message for keyword in regras_keywords):
        return """📋 **REGRAS DO QUIZ:**

1. **Responda as perguntas**: Você verá uma pergunta com várias opções de resposta. Escolha a opção que você acha correta.

2. **Pontuação**: Você ganha 1 ponto por cada resposta correta.

3. **Resultado final**: Ao final, você verá a quantidade de respostas corretas e sua pontuação total.

4. **Reiniciar**: Você pode tentar o quiz novamente para melhorar sua pontuação.

Está pronto para começar? 🎮"""
    
    elif any(keyword in message for keyword in sobre_keywords):
        return """🎶 **SOBRE O MELODIA MÁGICA:**

Bem-vindo ao nosso Quiz Melodia Mágica! 🎉✨

Aqui, as crianças podem aprender sobre música de maneira divertida e interativa, testando seus conhecimentos com perguntas sobre instrumentos musicais, sons, e muito mais!

Nosso quiz foi criado especialmente para os pequenos, com perguntas fáceis e divertidas que tornam o aprendizado um verdadeiro jogo.

**Características:**
• Perguntas sobre instrumentos musicais
• Sons e melodias
• Aprendizado divertido
• Interface amigável para crianças

Quer saber mais sobre as regras? 🎵"""
    
    elif any(keyword in message for keyword in ajuda_keywords):
        return """🤖 **COMO POSSO TE AJUDAR:**

Posso responder suas dúvidas sobre:

• **Regras do jogo** - Como jogar e pontuar
• **Sobre o projeto** - Informações sobre o Melodia Mágica
• **Saudações** - Para conversar comigo

Basta me perguntar sobre qualquer um desses tópicos! 😊"""
    
    else:
        return """🤔 Não entendi sua pergunta. 

Posso te ajudar com:
• Regras do jogo
• Informações sobre o Melodia Mágica
• Como jogar

Tente perguntar de outra forma! 😊"""

@csrf_exempt
def chat_message(request):
    """View para processar mensagens do chatbot"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'error': 'Mensagem vazia'}, status=400)
            
            # Gerar resposta do chatbot
            response = get_chatbot_response(message)
            
            # Gerar session_id se não existir
            session_id = data.get('session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Salvar mensagem no banco de dados
            user = request.user if request.user.is_authenticated else None
            ChatMessage.objects.create(
                user=user,
                message=message,
                response=response,
                session_id=session_id
            )
            
            return JsonResponse({
                'response': response,
                'session_id': session_id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

def chat_history(request):
    """View para obter histórico de conversas do usuário"""
    if request.user.is_authenticated:
        messages = ChatMessage.objects.filter(user=request.user)[:10]
        history = [{'message': msg.message, 'response': msg.response, 'timestamp': msg.timestamp} for msg in messages]
        return JsonResponse({'history': history})
    return JsonResponse({'history': []})
