FROM alpine:3.20

RUN apk add --no-cache python3 py3-pip

# Set working directory
WORKDIR /app

# Copy dependency file first for layer caching
COPY pyproject.toml .

# Install dependencies
RUN pip3 install --no-cache-dir --break-system-packages -e .

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Entrypoint
ENTRYPOINT ["python3", "main.py"]
