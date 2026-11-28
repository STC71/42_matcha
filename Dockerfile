# ============================================================
# Matcha - Dockerfile
# Imagen base ligera de Python 3.12
# ============================================================

FROM python:3.12-slim

# Instalamos dependencias del sistema necesarias para psycopg2 y Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Primero copiamos solo requirements para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Creamos la carpeta de uploads con permisos correctos
RUN mkdir -p uploads && chmod 755 uploads

# Creamos un usuario no-root por seguridad

EXPOSE 5000

# Usamos gunicorn + eventlet para soportar WebSockets (SocketIO)
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "--reload", "wsgi:app"]

#============================================================
# En resumen, qué hace este archivo:
# Define cómo se construye la imagen de la aplicación. 
# Usa Python 3.12, instala las librerías del sistema necesarias, 
# crea un usuario no-root (buena práctica de seguridad) 
# y arranca la app con Gunicorn + eventlet (necesario para el chat en tiempo real).
#============================================================