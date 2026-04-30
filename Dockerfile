FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser -m appuser

# Copy pre-downloaded wheels and requirements
COPY wheels/ ./wheels/
COPY requirements.txt .

# Install from local wheels — no internet access required
RUN pip install --no-cache-dir --no-index --find-links=./wheels -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Copy application files
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser test_app.py .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
