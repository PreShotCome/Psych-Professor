#!/usr/bin/env bash
# Start backend + frontend dev servers side by side
set -e

# Load .env if present
[ -f .env ] && export $(grep -v '^#' .env | xargs)

echo "Starting PsychBrain dev servers..."
echo "  Backend  → http://localhost:8000"
echo "  Frontend → http://localhost:5173"
echo "  API docs → http://localhost:8000/api/docs"
echo ""

# Start FastAPI in background
uvicorn api.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Vite dev server in foreground
cd frontend && npm run dev

# Kill backend when Vite exits
kill $BACKEND_PID 2>/dev/null || true
