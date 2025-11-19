# Dockerfile.warehouse-schema-init
FROM python:3.12-slim

# System prep (optional but good practice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install your Python deps here (no need to do it at runtime)
RUN pip install --no-cache-dir psycopg2-binary

# If you want the script baked into the image:
# COPY init_star_schema.py .

# Default command (can be overridden in compose if you like)
CMD ["python", "/app/init_star_schema.py"]
