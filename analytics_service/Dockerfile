FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip uninstall -y kafka-python 2>/dev/null || true

COPY . .

CMD ["python", "main.py"]