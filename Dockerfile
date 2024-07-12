# Use uma imagem base com Python 3.11
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências listadas em requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos da aplicação para o diretório de trabalho
COPY . .

# Expõe a porta em que a aplicação irá rodar
EXPOSE 5000

# Define a variável de ambiente para o Flask
ENV FLASK_APP=main.py

# Comando para rodar a aplicação usando o Gunicorn
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
CMD ["python", "main.py"]
