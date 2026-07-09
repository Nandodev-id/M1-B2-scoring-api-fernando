# Dockerfile — M1-B2 Pyrenex Risk API

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Create non-root user expected by the brief
RUN adduser --disabled-password --gecos "" --uid 1000 appuser

WORKDIR /home/appuser/app

# Dependencies first for Docker layer cache
COPY --chown=appuser:appuser requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Application code + packaged model
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser models/ ./models/

# Logs folder must be writable by appuser
RUN mkdir -p logs && chown -R appuser:appuser /home/appuser/app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
