# ==================================================
# Dockerfile
# Imagen de Docker para TechBot API.
# Usa Python 3.11 slim para mantener la imagen liviana.
# ==================================================

# -- Imagen base ----------------------------------
FROM python:3.11-slim

# -- Variables de entorno -------------------------
# Evita que Python genere archivos .pyc innecesarios
ENV PYTHONDONTWRITEBYTECODE=1
# Evita buffering en logs — los muestra en tiempo real
ENV PYTHONUNBUFFERED=1

# -- Directorio de trabajo ------------------------
WORKDIR /app

# -- Dependencias del sistema ---------------------
# psycopg2 necesita libpq-dev para compilar
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# -- Dependencias Python --------------------------
# Copia primero solo requirements para aprovechar cache de Docker
# Si no cambia requirements.txt no reinstala todo
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -- Codigo de la aplicacion ----------------------
COPY . .

# -- Puerto expuesto ------------------------------
EXPOSE 8000

# -- Comando de inicio ----------------------------
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
