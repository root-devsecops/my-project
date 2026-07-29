# ── Stage 1: Builder ──────────────────────────────
FROM python:3.12-alpine AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Production ───────────────────────────
FROM python:3.12-alpine AS production

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app.py .
COPY requirements.txt .

# Create non-root user
RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5000/health || exit 1

CMD ["python", "app.py"]