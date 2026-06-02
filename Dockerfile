# Imagen base de Python
FROM python:3.14-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

<<<<<<< HEAD
# Copiar todo el código del proyecto
=======
# Copiar_todo el código del proyecto
>>>>>>> dev-mathias
COPY . .

# Exponer el puerto
EXPOSE 5000

# Variable de entorno para producción
ENV FLASK_ENV=production

# Ejecutar con Gunicorn (4 workers)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]