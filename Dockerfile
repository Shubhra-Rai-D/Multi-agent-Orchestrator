# 1. Base Image: Use official lightweight Python 3.10 runtime
FROM python:3.10-slim

# 2. Performance & Logging Configuration:
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk inside container
# - PYTHONUNBUFFERED: Ensures unbuffered console output for real-time interactive prompts
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Set working directory inside container
WORKDIR /app

# 4. Docker Layer Caching: Copy dependencies file first
# Docker caches this layer so rebuilding code changes doesn't re-download pip packages
COPY requirements.txt .

# 5. Install Python dependencies without storing pip download cache
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy application source code into the container
COPY . .

# 7. Default executable command to start the interactive CLI
CMD ["python", "main.py"]
