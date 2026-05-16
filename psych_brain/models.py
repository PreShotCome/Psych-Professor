"""
Core data models for the psychological profiling brain.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


# Trait names and their semantic poles
TRAIT_POLES = {
    "moral":        ("good",      "evil"),
    "law":          ("lawful",    "chaotic"),
    "aggression":   ("passive",   "aggressive"),
    "deception":    ("honest",    "deceptive"),
    "empathy":      ("cold",      "empathetic"),
    "dominance":    ("submissive","dominant"),
    "impulsivity":  ("measured",  "impulsive"),
    "curiosity":    ("incurious", "curious"),
    "paranoia":     ("trusting",  "paranoid"),
    "manipulation": ("direct",    "manipulative"),
}

TRAIT_NAMES = list(TRAIT_POLES.keys())


@dataclass
class TraitVector:
    """
    A 10-dimensional psychological trait vector.
    Each trait is in [-1.0, 1.0] where the sign maps to TRAIT_POLES.
    moral/law: negative = first pole (good/lawful), positive = second (evil/chaotic)
    All others: negative = first pole (passive/honest/etc), positive = second
    """
    moral:        float = 0.0
    law:          float = 0.0
    aggression:   float = 0.0
    deception:    float = 0.0
    empathy:      float = 0.0
    dominance:    float = 0.0
    impulsivity:  float = 0.0
    curiosity:    float = 0.0
    paranoia:     float = 0.0
    manipulation: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {t: getattr(self, t) for t in TRAIT_NAMES}

    @classmethod
    def from_dict(cls, d: dict[str, float]) -> TraitVector:
        return cls(**{k: float(d.get(k, 0.0)) for k in TRAIT_NAMES})

    def blend(self, other: TraitVector, weight: float = 0.3) -> TraitVector:
        """Return a new vector blended toward `other` with given weight (0-1)."""
        blended = {}
        for t in TRAIT_NAMES:
            current = getattr(self, t)
            delta = getattr(other, t)
            blended[t] = max(-1.0, min(1.0, current + (delta - current) * weight))
        return TraitVector(**blended)

    def divergence(self, other: TraitVector) -> float:
        """Mean absolute difference across all traits (0-1)."""
        diffs = [abs(getattr(self, t) - getattr(other, t)) / 2.0 for t in TRAIT_NAMES]
        return sum(diffs) / len(diffs)

    def dominant_traits(self, threshold: float = 0.4) -> list[tuple[str, str, float]]:
        """Return (trait, pole_label, strength) for traits above threshold."""
        result = []
        for t in TRAIT_NAMES:
            v = getattr(self, t)
            if abs(v) >= threshold:
                poles = TRAIT_POLES[t]
                pole = poles[1] if v > 0 else poles[0]
                result.append((t, pole, abs(v)))
        result.sort(key=lambda x: -x[2])
        return result


@dataclass
class InteractionRecord:
    """A single analyzed message exchange."""
    timestamp: float
    message: str
    signals: dict[str, float]      # raw trait signals extracted from this message
    notes: str                     # analyzer's brief reasoning


@dataclass
class SessionProfile:
    """
    Profile for a single gameplay session / run.
    Tracks behavior independent of the player's lifetime history.
    """
    session_id: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    traits: TraitVector = field(default_factory=TraitVector)
    interaction_count: int = 0
    interactions: list[InteractionRecord] = field(default_factory=list)
    session_notes: str = ""        # free-form summary updated each turn

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "traits": self.traits.to_dict(),
            "interaction_count": self.interaction_count,
            "interactions": [
                {
                    "timestamp": r.timestamp,
                    "message": r.message,
                    "signals": r.signals,
                    "notes": r.notes,
                }
                for r in self.interactions
            ],
            "session_notes": self.session_notes,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SessionProfile:
        interactions = [
            InteractionRecord(
                timestamp=r["timestamp"],
                message=r["message"],
                signals=r["signals"],
                notes=r["notes"],
            )
            for r in d.get("interactions", [])
        ]
        return cls(
            session_id=d["session_id"],
            start_time=d.get("start_time", 0.0),
            end_time=d.get("end_time"),
            traits=TraitVector.from_dict(d.get("traits", {})),
            interaction_count=d.get("interaction_count", 0),
            interactions=interactions,
            session_notes=d.get("session_notes", ""),
        )


@dataclass
class UserProfile:
    """
    Persistent profile for a player across all sessions.
    Lifetime traits are a slow-moving average; sessions capture individual runs.
    """
    user_id: str
    display_name: str
    created_at: float = field(default_factory=time.time)
    lifetime_traits: TraitVector = field(default_factory=TraitVector)
    session_count: int = 0
    total_interactions: int = 0
    sessions: list[SessionProfile] = field(default_factory=list)
    archetype: str = ""            # e.g. "calculating villain", "reluctant hero"

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "created_at": self.created_at,
            "lifetime_traits": self.lifetime_traits.to_dict(),
            "session_count": self.session_count,
            "total_interactions": self.total_interactions,
            "sessions": [s.to_dict() for s in self.sessions],
            "archetype": self.archetype,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> UserProfile:
        sessions = [SessionProfile.from_dict(s) for s in d.get("sessions", [])]
        return cls(
            user_id=d["user_id"],
            display_name=d.get("display_name", d["user_id"]),
            created_at=d.get("created_at", time.time()),
            lifetime_traits=TraitVector.from_dict(d.get("lifetime_traits", {})),
            session_count=d.get("session_count", 0),
            total_interactions=d.get("total_interactions", 0),
            sessions=sessions,
            archetype=d.get("archetype", ""),
        )
