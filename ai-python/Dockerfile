FROM python:3.12-slim
WORKDIR /app
COPY ai_service.py .
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "ai_service.py"]
