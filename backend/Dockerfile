FROM python:3.9-slim

WORKDIR /app

# Copiar los archivos de requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias y la biblioteca schedule para tareas programadas
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear la base de datos y cargar datos iniciales
RUN python create_db.py && python seed_dataV2.py

# Exponer el puerto
EXPOSE 8000

# Crear un script de inicio para ejecutar tanto el servidor como el entrenamiento programado
RUN echo '#!/bin/bash\npython scheduled_training.py &\nuvicorn main:app --host 0.0.0.0 --port 8000' > start.sh && \
    chmod +x start.sh

# Comando para ejecutar la aplicación
CMD ["/app/start.sh"]
