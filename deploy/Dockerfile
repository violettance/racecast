# Python runtime
FROM python:3.9-slim

# Set workdir
WORKDIR /app

# System deps (optional but helpful for scientific stack)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
# Note: avoid copying large caches (see .dockerignore)
COPY . .

# Env defaults
ENV PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


