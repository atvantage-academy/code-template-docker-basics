FROM python:3.12-slim
WORKDIR /app

# Erst die Abhängigkeiten, dann der Code: Eine Änderung an app.py soll die
# Installation nicht erneut auslösen.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8080
CMD ["python", "app.py"]
