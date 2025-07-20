# Alternative Docker deployment
FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Use shell form to allow environment variable expansion
CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} 