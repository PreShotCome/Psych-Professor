"""
Session manager — handles the lifecycle of a single gameplay run.
"""
from __future__ import annotations

import time
import uuid

from .models import SessionProfile, TraitVector, InteractionRecord


# How much each new message shifts the session trait vector (0=never updates, 1=instant)
SESSION_LEARNING_RATE = 0.35

# How many interactions before the session traits are considered "established"
WARMUP_INTERACTIONS = 3


class SessionManager:
    def __init__(self, session_id: str | None = None):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.profile = SessionProfile(session_id=self.session_id)

    def record_interaction(self, message: str, signals: TraitVector, notes: str) -> None:
        """Incorporate one interaction's signals into the session profile."""
        record = InteractionRecord(
            timestamp=time.time(),
            message=message,
            signals=signals.to_dict(),
            notes=notes,
        )
        self.profile.interactions.append(record)
        self.profile.interaction_count += 1

        # Blend signals into session traits; weight grows until warmup is complete
        effective_rate = min(
            SESSION_LEARNING_RATE,
            SESSION_LEARNING_RATE * (self.profile.interaction_count / WARMUP_INTERACTIONS),
        )
        self.profile.traits = self.profile.traits.blend(signals, weight=effective_rate)

    def update_notes(self, notes: str) -> None:
        self.profile.session_notes = notes

    def close(self) -> SessionProfile:
        self.profile.end_time = time.time()
        return self.profile
