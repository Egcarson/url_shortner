# Dockerfile

# Use a lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy the full app
COPY . .

# Run the app with uvicorn
CMD ["uvicorn", "src:app", "--host", "0.0.0.0", "--port", "8000"]
