import requests
import json
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class N8nService:
    """Serviço para comunicação com n8n"""
    
    def __init__(self):
        # URL do webhook do n8n (carregada do .env via settings)
        self.webhook_url = settings.N8N_WEBHOOK_URL
        self.timeout = 30  # timeout de 30 segundos
    
    def send_message_to_n8n(self, message, session_id=None, user_id=None):
        """
        Envia mensagem para o n8n e retorna a resposta da LLM
        
        Args:
            message (str): Mensagem do usuário
            session_id (str): ID da sessão do chat
            user_id (int): ID do usuário (opcional)
            
        Returns:
            dict: Resposta contendo 'response' e 'success'
        """
        try:
            payload = {
                'message': message,
                'session_id': session_id,
                'user_id': user_id,
                'timestamp': str(timezone.now())
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'MelodiaMagica-Chatbot/1.0'
            }
            
            logger.info(f"=== ENVIANDO PARA N8N ===")
            logger.info(f"URL: {self.webhook_url}")
            logger.info(f"Mensagem: {message[:100]}...")
            logger.info(f"Session ID: {session_id}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            logger.info(f"Headers: {headers}")
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            logger.info(f"=== RESPOSTA DO N8N ===")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Headers da resposta: {dict(response.headers)}")
            logger.info(f"Conteúdo da resposta: {response.text[:500]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Algumas execuções do n8n retornam uma lista de itens.
                    # Se for o caso, usamos o primeiro item.
                    if isinstance(data, list):
                        logger.info("Resposta do n8n é uma lista; usando primeiro item")
                        if len(data) > 0:
                            data = data[0]
                        else:
                            logger.warning("Lista vazia recebida do n8n; usando fallback")
                            return self._fallback_response()
                    logger.info(f"JSON parseado com sucesso: {json.dumps(data, indent=2)}")
                    
                    # Verificar se há erro na resposta do n8n
                    if 'error' in data:
                        error_type = data.get('error')
                        logger.warning(f"N8N retornou erro: {error_type}")
                        
                        # Se for erro de mensagem vazia ou webhook não registrado, usar fallback
                        if error_type in ['empty_message', 'webhook_not_registered', 'unknown_webhook']:
                            logger.warning(f"Erro conhecido do n8n ({error_type}), usando fallback")
                            return self._fallback_response()
                    
                    # Verificar se a resposta contém conteúdo válido
                    # Alguns nós do n8n retornam o texto em 'output' ou 'text'
                    response_text = (
                        data.get('response')
                        or data.get('output')
                        or data.get('text')
                        or ''
                    )
                    if isinstance(response_text, str):
                        response_text = response_text.strip()
                    else:
                        response_text = str(response_text).strip()
                    if not response_text or response_text == "Desculpe, não recebi sua mensagem. Tente novamente! 😊":
                        logger.warning("Resposta do n8n está vazia ou é mensagem de erro padrão, usando fallback")
                        return self._fallback_response()
                    
                    return {
                        'success': True,
                        'response': response_text,
                        'session_id': data.get('session_id', session_id)
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"ERRO: Resposta do n8n não é um JSON válido - {str(e)}")
                    logger.error(f"Conteúdo completo da resposta: {response.text}")
                    return self._fallback_response()
            else:
                logger.error(f"ERRO: Status code não é 200 - {response.status_code}")
                logger.error(f"Texto da resposta de erro: {response.text}")
                return self._fallback_response()
                
        except requests.exceptions.Timeout as e:
            logger.error(f"ERRO: Timeout na comunicação com n8n - {str(e)}")
            logger.error(f"URL que deu timeout: {self.webhook_url}")
            logger.error(f"Timeout configurado: {self.timeout} segundos")
            return self._fallback_response()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"ERRO: Erro de conexão com n8n - {str(e)}")
            logger.error(f"URL de conexão: {self.webhook_url}")
            logger.error(f"Verifique se o n8n está rodando na porta correta")
            return self._fallback_response()
        except requests.exceptions.RequestException as e:
            logger.error(f"ERRO: Erro na requisição HTTP - {str(e)}")
            logger.error(f"Tipo do erro: {type(e).__name__}")
            return self._fallback_response()
        except Exception as e:
            logger.error(f"ERRO: Erro inesperado na comunicação com n8n - {str(e)}")
            logger.error(f"Tipo do erro: {type(e).__name__}")
            logger.error(f"Payload que causou o erro: {json.dumps(payload, indent=2)}")
            import traceback
            logger.error(f"Stack trace completo: {traceback.format_exc()}")
            return self._fallback_response()
    
    def _fallback_response(self):
        """Resposta de fallback quando n8n não está disponível"""
        return {
            'success': False,
            'response': """🤖 Desculpe, estou com dificuldades técnicas no momento.

Tente novamente em alguns instantes! 😊"""
        }
    
    def health_check(self):
        """Verifica se o n8n está respondendo"""
        try:
            logger.info(f"=== HEALTH CHECK N8N ===")
            logger.info(f"Testando conectividade com: {self.webhook_url}")
            
            # Tenta fazer uma requisição simples para verificar conectividade
            test_payload = {'test': True, 'message': 'health_check'}
            response = requests.post(
                self.webhook_url,
                json=test_payload,
                timeout=5
            )
            
            logger.info(f"Health check - Status: {response.status_code}")
            logger.info(f"Health check - Resposta: {response.text[:200]}...")
            
            is_healthy = response.status_code == 200
            logger.info(f"N8N está {'saudável' if is_healthy else 'com problemas'}")
            
            return is_healthy
        except Exception as e:
            logger.error(f"ERRO no health check: {str(e)}")
            logger.error(f"Tipo do erro: {type(e).__name__}")
            return False