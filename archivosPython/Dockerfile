FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Display logs immediately
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

RUN mkdir -p /app/staticfiles

# Expose Django port
EXPOSE 8000

# Run Django
# Por defecto arranca con start.sh (migraciones + estáticos + Gunicorn).
# docker-compose.yml sobreescribe este comando para el despliegue local.
CMD ["./start.sh"]