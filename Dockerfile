# ── Stage 1: Build React PWA ────────────────────────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python API + built frontend ─────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY psych_brain/ ./psych_brain/
COPY api/ ./api/
COPY main.py ./

COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Profiles directory — mount a persistent disk here in production
RUN mkdir -p /data/profiles
ENV PROFILES_DIR=/data/profiles

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
