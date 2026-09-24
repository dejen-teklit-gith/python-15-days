# ---- Build a small, reproducible image for the churn API ----
FROM python:3.12-slim

# Don't write .pyc files; flush logs immediately (important in containers)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /service

# 1) Dependencies first → Docker caches this layer until requirements change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Code + data, then train INSIDE the build → the image always contains a model
COPY train.py .
COPY data ./data
COPY app ./app
RUN python train.py

# 3) Run as a non-root user (security basic)
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
