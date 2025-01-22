FROM python:3.11-slim

# Specifying ENV variable for URI in Cloud Run instead of Dockerfile

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]
