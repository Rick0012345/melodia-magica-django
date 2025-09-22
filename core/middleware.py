from django.core.cache import cache
from django.utils.cache import get_cache_key, learn_cache_key
from django.conf import settings
import hashlib
import json

class CacheMiddleware:
    """
    Middleware para cachear respostas de páginas que não mudam frequentemente
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Não cachear para usuários autenticados ou requests POST
        if request.user.is_authenticated or request.method != 'GET':
            return self.get_response(request)
            
        # Gerar chave de cache baseada na URL e parâmetros
        cache_key = self._get_cache_key(request)
        
        # Tentar obter resposta do cache
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
            
        # Se não estiver no cache, processar normalmente
        response = self.get_response(request)
        
        # Cachear apenas respostas bem-sucedidas
        if response.status_code == 200:
            # Definir tempo de cache baseado no tipo de página
            cache_timeout = self._get_cache_timeout(request.path)
            cache.set(cache_key, response, cache_timeout)
            
        return response
    
    def _get_cache_key(self, request):
        """Gera uma chave única para o cache baseada na URL e parâmetros"""
        # Incluir URL e parâmetros GET na chave
        key_data = {
            'url': request.path,
            'params': dict(request.GET.items()),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100]
        }
        
        # Criar hash da chave
        key_string = json.dumps(key_data, sort_keys=True)
        return f"page_cache:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _get_cache_timeout(self, path):
        """Define tempo de cache baseado no tipo de página"""
        # Páginas estáticas podem ser cacheadas por mais tempo
        if path in ['/', '/servicos/', '/contato/']:
            return 300  # 5 minutos
        elif path.startswith('/static/') or path.startswith('/media/'):
            return 3600  # 1 hora
        else:
            return 60  # 1 minuto para outras páginas


class DatabaseOptimizationMiddleware:
    """
    Middleware para otimizar consultas ao banco de dados
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Adicionar headers para otimização
        response = self.get_response(request)
        
        # Adicionar headers de cache para recursos estáticos
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            response['Cache-Control'] = 'public, max-age=31536000, immutable'
            response['Expires'] = 'Thu, 31 Dec 2024 23:59:59 GMT'
        
        # Adicionar headers de compressão
        response['Vary'] = 'Accept-Encoding'
        
        return response


class PerformanceMonitoringMiddleware:
    """
    Middleware para monitorar performance das requisições
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        import time
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Calcular tempo de processamento
        processing_time = time.time() - start_time
        
        # Adicionar header com tempo de processamento (apenas em debug)
        if settings.DEBUG:
            response['X-Processing-Time'] = f"{processing_time:.3f}s"
            
            # Log de requisições lentas
            if processing_time > 1.0:  # Mais de 1 segundo
                print(f"Requisição lenta detectada: {request.path} - {processing_time:.3f}s")
        
        return response 