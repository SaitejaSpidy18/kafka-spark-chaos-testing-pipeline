FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for producer counter file (mounted as volume in future if needed)
RUN mkdir -p /data

# Copy application code
COPY main.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
