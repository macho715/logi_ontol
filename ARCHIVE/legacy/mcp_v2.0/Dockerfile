FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY src/ ./src/

# Copy TTL data
COPY data/hvdc_data.ttl ./data/hvdc_data.ttl

# Expose port
EXPOSE 8000

# Environment variables
ENV TTL_PATH=/app/data/hvdc_data.ttl
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=8000
ENV PYTHONPATH=/app

# Run server
CMD ["python", "-m", "uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]


