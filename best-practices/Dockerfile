FROM python:3.12-slim
WORKDIR /app

# Zuerst nur die Abhängigkeitsliste: Solange sie sich nicht ändert, bleibt die
# Installation im Cache – egal, wie oft app.py sich ändert.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["python", "app.py"]
