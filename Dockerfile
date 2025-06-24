# Use Python 3.12 slim base
FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . .

# Set default command to run FastAPI app on port 8080 (Cloud Run standard)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

