from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
import uuid
import logging
from .models import ChatMessage
from .n8n_service import N8nService

logger = logging.getLogger(__name__)

def get_chatbot_response(message):
    """Função de fallback simples quando n8n não está disponível"""
    return """🤖 Desculpe, estou com dificuldades técnicas no momento. 
    
Posso te ajudar com informações básicas sobre o Melodia Mágica:
• É um quiz musical educativo para crianças
• Teste seus conhecimentos sobre instrumentos musicais
• Aprenda de forma divertida e interativa

Tente novamente em alguns instantes! 😊"""

@csrf_exempt
def chat_message(request):
    """View para processar mensagens do chatbot com integração n8n"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'error': 'Mensagem vazia'}, status=400)
            
            # Gerar session_id se não existir
            session_id = data.get('session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Verificar se deve usar n8n ou fallback
            use_n8n = getattr(settings, 'USE_N8N_CHATBOT', True)
            
            if use_n8n:
                # Usar n8n com LLM
                n8n_service = N8nService()
                user_id = request.user.id if request.user.is_authenticated else None
                
                logger.info(f"Enviando mensagem para n8n: {message[:50]}...")
                result = n8n_service.send_message_to_n8n(message, session_id, user_id)
                
                if result['success']:
                    response = result['response']
                    logger.info("Resposta recebida do n8n com sucesso")
                else:
                    # Se n8n falhou, usar chatbot local como fallback
                    response = get_chatbot_response(message)
                    logger.warning("N8n falhou, usando chatbot local como fallback")
            else:
                # Usar chatbot local como fallback
                response = get_chatbot_response(message)
                logger.info("Usando chatbot local (n8n desabilitado)")
            
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
                'session_id': session_id,
                'source': 'n8n' if use_n8n else 'local'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            logger.error(f"Erro no chat_message: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

def chat_history(request):
    """View para obter histórico de conversas do usuário"""
    if request.user.is_authenticated:
        messages = ChatMessage.objects.filter(user=request.user)[:10]
        history = [{'message': msg.message, 'response': msg.response, 'timestamp': msg.timestamp} for msg in messages]
        return JsonResponse({'history': history})
    return JsonResponse({'history': []})
