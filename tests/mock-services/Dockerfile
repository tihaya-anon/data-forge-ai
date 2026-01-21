FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mock-llm.py .
EXPOSE 8000
CMD ["python", "mock-llm.py"]
