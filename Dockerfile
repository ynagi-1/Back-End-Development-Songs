FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt greenlet==3.1.1
COPY . .
EXPOSE 8080
USER 1001
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
