# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first to maximize layer cache reuse.
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

# Copy application source.
COPY bot.py ./
COPY functions ./functions

# Run as non-root user.
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
	&& chown -R appuser:appuser /app
USER appuser

# Pass environment variables at runtime (for example: --env-file .env).
CMD ["python", "bot.py"]