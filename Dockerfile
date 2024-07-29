FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al directorio de trabajo
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido del proyecto al directorio de trabajo
COPY . .

# Expone el puerto en el que correrá la aplicación
EXPOSE 8082

# Define el comando para correr la aplicación
CMD ["python", "main.py"]
