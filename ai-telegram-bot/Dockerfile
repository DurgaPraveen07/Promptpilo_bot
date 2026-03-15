FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies (required for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Ensure directories exist
RUN mkdir -p data chroma_db static

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI server (which automatically runs the Telegram bot in background)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
