#!/bin/bash

# Aguardar o banco de dados estar disponível
echo "Aguardando banco de dados..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Banco de dados disponível!"

# Executar migrações
echo "Executando makemigrations..."
python manage.py makemigrations

echo "Executando migrate..."
python manage.py migrate

# Criar superusuário se não existir
echo "Criando superusuário..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '123')
    print('Superusuário criado: admin/123')
else:
    print('Superusuário já existe')
"

echo "Inicialização concluída!"

# Iniciar servidor
exec python manage.py runserver 0.0.0.0:8000