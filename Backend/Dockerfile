# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del backend
COPY . .

# Exponer el puerto 8000
EXPOSE 8000

# Configurar variables de entorno (ajusta según tu configuración)
ENV MONGO_URI=mongodb://admin:admin123@mongodb:27017/
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar el servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]