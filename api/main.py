"""
FastAPI backend for the PsychBrain PWA — fully stateless.
Profile and session state live in the client (browser localStorage)
and travel with every request, so no server-side storage is needed.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from psych_brain import PsychBrain

NPC_PERSONA = os.environ.get(
    "NPC_PERSONA",
    "the Psych Professor — calm, unhurried, and precise. "
    "You've seen enough people to stop being surprised by them. "
    "You observe more than you speak, and when you do speak, you mean it.",
)
MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-7")

app = FastAPI(title="PsychBrain API", docs_url="/api/docs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ───────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_id: str
    display_name: str | None = None
    message: str
    profile: dict | None = None   # serialized UserProfile from localStorage
    session: dict | None = None   # serialized SessionProfile from localStorage
    history: list[dict] | None = None  # recent conversation [{role, content}]


class SessionRequest(BaseModel):
    user_id: str
    display_name: str | None = None
    profile: dict | None = None
    session: dict | None = None


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_brain(user_id: str, display_name: str | None, profile: dict | None, session: dict | None) -> PsychBrain:
    return PsychBrain.from_state(
        user_id=user_id,
        display_name=display_name,
        profile_dict=profile,
        session_dict=session,
        npc_persona=NPC_PERSONA,
        model=MODEL,
    )


# ── API routes ───────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/interview-questions")
def interview_questions():
    from psych_brain.questions import INTERVIEW_QUESTIONS
    return {"questions": INTERVIEW_QUESTIONS}


@app.post("/api/chat")
def chat(req: ChatRequest):
    brain = make_brain(req.user_id, req.display_name, req.profile, req.session)
    if brain._session is None:
        brain.start_session()
    result = brain.process(req.message, return_analysis=True, history=req.history)
    # Return analysis + updated client state
    return {**result, **brain.get_state()}


@app.post("/api/session/start")
def start_session(req: SessionRequest):
    brain = make_brain(req.user_id, req.display_name, req.profile, None)
    sid = brain.start_session()
    return {"session_id": sid, **brain.get_state()}


@app.post("/api/session/end")
def end_session(req: SessionRequest):
    brain = make_brain(req.user_id, req.display_name, req.profile, req.session)
    brain.end_session()
    return brain.get_state()


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
    return {"detail": "Frontend not built yet. Run: cd frontend && npm run build"}
