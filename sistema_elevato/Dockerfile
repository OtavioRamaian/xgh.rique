# Usa uma versão leve do Python
FROM python:3.11-slim

# Define a pasta de trabalho dentro do contêiner
WORKDIR /app

# Copia os requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o seu código para dentro do contêiner
COPY . .

# Libera a porta 5000
EXPOSE 5000

# Comando para rodar o sistema
CMD ["python", "app.py"]