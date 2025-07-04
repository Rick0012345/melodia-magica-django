FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Criar usuário não-root
RUN adduser --disabled-password --gecos '' appuser

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Mudar para usuário não-root
USER appuser

EXPOSE 8000

CMD ["python", "melodiaMagica/manage.py", "runserver", "0.0.0.0:8000"] 