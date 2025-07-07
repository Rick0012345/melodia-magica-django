#!/usr/bin/env python3
"""
Script para build de produção com todas as otimizações
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Executa um comando e mostra o resultado"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro em {description}:")
        print(e.stderr)
        return False

def main():
    print("🚀 Iniciando build de produção...")
    
    # Verificar se estamos no diretório correto
    if not Path('manage.py').exists():
        print("❌ Execute este script no diretório raiz do projeto Django")
        sys.exit(1)
    
    # 1. Coletar arquivos estáticos
    if not run_command("python manage.py collectstatic --noinput", "Coletando arquivos estáticos"):
        sys.exit(1)
    
    # 2. Otimizar imagens
    if Path('scripts/optimize_images.py').exists():
        if not run_command("python scripts/optimize_images.py", "Otimizando imagens"):
            print("⚠️  Otimização de imagens falhou, continuando...")
    
    # 3. Executar migrações
    if not run_command("python manage.py migrate", "Executando migrações"):
        sys.exit(1)
    
    # 4. Verificar configurações
    if not run_command("python manage.py check --deploy", "Verificando configurações de produção"):
        sys.exit(1)
    
    # 5. Criar diretório de logs se não existir
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # 6. Verificar se Redis está rodando (se estiver usando Docker)
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=1, socket_connect_timeout=1)
        r.ping()
        print("✅ Redis está rodando")
    except:
        print("⚠️  Redis não está rodando. Execute 'docker-compose up redis' se estiver usando Docker")
    
    print("\n🎉 Build de produção concluído!")
    print("\n📋 Próximos passos:")
    print("1. Configure as variáveis de ambiente de produção")
    print("2. Execute: python manage.py runserver --settings=melodiaMagica.settings_production")
    print("3. Ou use Gunicorn: gunicorn melodiaMagica.wsgi:application --settings=melodiaMagica.settings_production")

if __name__ == '__main__':
    main() 