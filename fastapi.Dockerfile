# FastAPI Dockerfile (lives in repo root)
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy requirements if you have them, else install inline
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy all code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
