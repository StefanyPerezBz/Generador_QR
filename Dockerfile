# --- Imagen base de Python ---
FROM python:3.11-slim

# --- Directorio de trabajo ---
WORKDIR /app

# --- Copiar archivos al contenedor ---
COPY . /app

# --- Instalar dependencias ---
RUN pip install --no-cache-dir -r requirements.txt

# --- Configurar variables de entorno ---
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_ENABLEXSRSFPROTECTION=false

# --- Exponer puerto ---
EXPOSE 8501

# --- Comando de inicio (por defecto el panel administrador) ---
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
CMD ["streamlit", "run", "view_media.py", "--server.port=8501", "--server.address=0.0.0.0"]
