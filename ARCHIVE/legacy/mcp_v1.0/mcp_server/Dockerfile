FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY . /app/mcp_server/

# Copy TTL data (assumes hvdc_data.ttl is in parent directory)
COPY ../sample_outputs/hvdc_data.ttl /app/sample_outputs/hvdc_data.ttl

# Expose port
EXPOSE 8000

# Environment variables
ENV TTL_PATH=/app/sample_outputs/hvdc_data.ttl
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=8000
ENV PYTHONPATH=/app

# Run server
CMD ["python", "-m", "uvicorn", "mcp_server.mcp_ttl_server:app", "--host", "0.0.0.0", "--port", "8000"]


