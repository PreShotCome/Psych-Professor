"""FastAPI backend for the PsychBrain PWA."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from psych_brain import PsychBrain
from psych_brain.storage import ProfileStorage

PROFILES_DIR = os.environ.get("PROFILES_DIR", "profiles")
MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-7")
NPC_PERSONA = os.environ.get(
    "NPC_PERSONA",
    "the Psych Professor — an ancient, all-knowing entity who has observed countless souls "
    "across lifetimes of choices. You see through every mask and persona instantly, "
    "watching patterns form and shift with quiet, unsettling clarity.",
)

app = FastAPI(title="PsychBrain API", docs_url="/api/docs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_brains: dict[str, PsychBrain] = {}


def get_brain(user_id: str, display_name: str | None = None) -> PsychBrain:
    if user_id not in _brains:
        _brains[user_id] = PsychBrain(
            user_id=user_id,
            display_name=display_name or user_id,
            npc_persona=NPC_PERSONA,
            profiles_dir=PROFILES_DIR,
            model=MODEL,
        )
    elif display_name:
        _brains[user_id].user_profile.display_name = display_name
    return _brains[user_id]


# ── Request models ───────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_id: str
    display_name: str | None = None
    message: str


class SessionRequest(BaseModel):
    user_id: str
    display_name: str | None = None


# ── API routes ───────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
def chat(req: ChatRequest):
    brain = get_brain(req.user_id, req.display_name)
    if brain._session is None:
        brain.start_session()
    return brain.process(req.message, return_analysis=True)


@app.post("/api/session/start")
def start_session(req: SessionRequest):
    brain = get_brain(req.user_id, req.display_name)
    if brain._session is not None:
        brain.end_session()
    sid = brain.start_session()
    return {
        "session_id": sid,
        "session_count": brain.user_profile.session_count,
    }


@app.post("/api/session/end")
def end_session(req: SessionRequest):
    brain = get_brain(req.user_id, req.display_name)
    brain.end_session()
    return {"status": "ended"}


@app.get("/api/profile/{user_id}")
def get_profile(user_id: str):
    return get_brain(user_id).get_profile_summary()


@app.get("/api/session/{user_id}")
def get_session(user_id: str):
    snap = get_brain(user_id).get_session_snapshot()
    return {"active": snap is not None, **(snap or {})}


@app.get("/api/users")
def list_users():
    return {"users": ProfileStorage(PROFILES_DIR).list_users()}


# ── Serve React SPA (must be last) ──────────────────────────────────────────

_DIST = Path("frontend/dist")


@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str):
    candidate = _DIST / full_path
    if candidate.exists() and candidate.is_file():
        return FileResponse(str(candidate))
    index = _DIST / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"error": "Frontend not built. Run: cd frontend && npm run build"}
