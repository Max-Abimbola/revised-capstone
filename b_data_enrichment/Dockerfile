FROM python:3.12

# Specifying ENV variable for URI in Cloud Run instead of Dockerfile

WORKDIR /b_data_enrichment

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]
