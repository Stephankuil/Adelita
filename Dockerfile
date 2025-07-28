# Gebruik een officiële Python image
FROM python:3.13-slim

# Zet de werkdirectory in de container
WORKDIR /app

# Kopieer alleen eerst requirements.txt om de layer te cachen (sneller bij rebuilds)
COPY requirements.txt .

# Installeer dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de rest van de app-code
COPY . .

# Open poort 8080
EXPOSE 8080

# Start de Flask-app met gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]

