# Builder stage (install deps)
FROM python:3.11-slim AS builder
WORKDIR /app
# Copy only requirements to leverage cache
COPY requirements.txt .
RUN pip wheel --wheel-dir=/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim
WORKDIR /app
# Create non-root user
RUN useradd -m appuser
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt
COPY src/ /app/
USER appuser
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8080/health || exit 1
ENTRYPOINT ["python", "main.py"]