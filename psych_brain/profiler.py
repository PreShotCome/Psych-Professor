"""
The Brain — main orchestrator that ties analysis, sessions, and persistence together.
"""
from __future__ import annotations

import time

from .analyzer import PsychAnalyzer
from .models import UserProfile, SessionProfile, TraitVector
from .session import SessionManager
from .storage import ProfileStorage


# How much each completed session shifts lifetime traits (slow-moving)
LIFETIME_LEARNING_RATE = 0.12

# How many sessions before we re-derive the archetype label
ARCHETYPE_REFRESH_SESSIONS = 3


class PsychBrain:
    """
    Main interface for the AI psychological learning system.

    Usage:
        brain = PsychBrain(user_id="player_123", display_name="Alex")
        brain.start_session()
        response = brain.process("I want to burn the village down.")
        brain.end_session()
    """

    def __init__(
        self,
        user_id: str,
        display_name: str | None = None,
        npc_persona: str = "a wise and perceptive stranger",
        profiles_dir: str = "profiles",
        model: str = "claude-opus-4-7",
    ):
        self.storage = ProfileStorage(profiles_dir)
        self.analyzer = PsychAnalyzer(model=model)
        self.npc_persona = npc_persona

        existing = self.storage.load(user_id)
        if existing:
            self.user_profile = existing
            if display_name:
                self.user_profile.display_name = display_name
        else:
            self.user_profile = UserProfile(
                user_id=user_id,
                display_name=display_name or user_id,
            )

        self._session: SessionManager | None = None

    @classmethod
    def from_state(
        cls,
        user_id: str,
        display_name: str | None,
        profile_dict: dict | None,
        session_dict: dict | None,
        npc_persona: str,
        model: str,
    ) -> "PsychBrain":
        """Create a stateless brain from serialized client state — no disk I/O."""
        brain: PsychBrain = object.__new__(cls)
        brain.storage = None
        brain.npc_persona = npc_persona
        brain.analyzer = PsychAnalyzer(model=model)

        if profile_dict:
            brain.user_profile = UserProfile.from_dict(profile_dict)
            if display_name:
                brain.user_profile.display_name = display_name
        else:
            brain.user_profile = UserProfile(
                user_id=user_id,
                display_name=display_name or user_id,
            )

        if session_dict:
            brain._session = SessionManager(
                session_id=session_dict.get("session_id"),
                existing_profile=SessionProfile.from_dict(session_dict),
            )
        else:
            brain._session = None

        return brain

    def get_state(self) -> dict:
        """Return serializable state for the client to store locally."""
        return {
            "profile": self.user_profile.to_dict(),
            "session": self._session.profile.to_dict() if self._session else None,
        }

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def start_session(self, session_id: str | None = None) -> str:
        """Begin a new gameplay session. Returns the session ID."""
        if self._session is not None:
            self.end_session()
        self._session = SessionManager(session_id=session_id)
        self.user_profile.session_count += 1
        return self._session.session_id

    def end_session(self) -> None:
        """Close the session, merge into lifetime profile, and persist."""
        if self._session is None:
            return

        completed = self._session.close()
        self.user_profile.sessions.append(completed)

        # Blend session traits into lifetime traits slowly
        if completed.interaction_count > 0:
            self.user_profile.lifetime_traits = self.user_profile.lifetime_traits.blend(
                completed.traits, weight=LIFETIME_LEARNING_RATE
            )

        # Refresh archetype periodically
        if (
            self.user_profile.session_count % ARCHETYPE_REFRESH_SESSIONS == 0
            or not self.user_profile.archetype
        ) and self.user_profile.total_interactions >= 3:
            self.user_profile.archetype = self.analyzer.generate_archetype(self.user_profile)

        if self.storage:
            self.storage.save(self.user_profile)
        self._session = None

    # ------------------------------------------------------------------
    # Core processing
    # ------------------------------------------------------------------

    def process(self, message: str, return_analysis: bool = False) -> str | dict:
        """
        Process a player message:
        1. Extract psychological signals
        2. Update session profile
        3. Generate a psychologically-aware NPC response

        If return_analysis=True, returns a dict with the response + debug info.
        """
        if self._session is None:
            self.start_session()

        signals, notes = self.analyzer.extract_signals(
            message,
            context=self._session.profile.session_notes,
        )

        self._session.record_interaction(message, signals, notes)
        self.user_profile.total_interactions += 1

        # Build a running session note for context in subsequent turns
        session_summary = self._build_session_summary()
        self._session.update_notes(session_summary)

        response = self.analyzer.generate_response(
            message=message,
            user_profile=self.user_profile,
            session=self._session.profile,
            npc_persona=self.npc_persona,
        )

        if self.storage:
            self.storage.save(self.user_profile)

        if return_analysis:
            lt = self.user_profile.lifetime_traits
            st = self._session.profile.traits
            return {
                "response": response,
                "signals_this_turn": signals.to_dict(),
                "signal_notes": notes,
                "session_traits": st.to_dict(),
                "lifetime_traits": lt.to_dict(),
                "divergence": round(lt.divergence(st), 3),
                "session_dominant": st.dominant_traits(0.3),
                "lifetime_dominant": lt.dominant_traits(0.3),
                "archetype": self.user_profile.archetype,
                "interaction_count": self._session.profile.interaction_count,
            }

        return response

    # ------------------------------------------------------------------
    # Introspection helpers (useful for game UI / debug)
    # ------------------------------------------------------------------

    def get_session_snapshot(self) -> dict | None:
        """Return a summary of the current session state."""
        if self._session is None:
            return None
        st = self._session.profile.traits
        lt = self.user_profile.lifetime_traits
        return {
            "session_id": self._session.session_id,
            "interaction_count": self._session.profile.interaction_count,
            "session_traits": st.to_dict(),
            "session_dominant": st.dominant_traits(0.3),
            "lifetime_traits": lt.to_dict(),
            "lifetime_dominant": lt.dominant_traits(0.3),
            "divergence": round(lt.divergence(st), 3),
            "archetype": self.user_profile.archetype,
            "session_notes": self._session.profile.session_notes,
        }

    def get_profile_summary(self) -> dict:
        """Return a clean summary of the player's full profile."""
        lt = self.user_profile.lifetime_traits
        return {
            "user_id": self.user_profile.user_id,
            "display_name": self.user_profile.display_name,
            "archetype": self.user_profile.archetype or "undefined",
            "session_count": self.user_profile.session_count,
            "total_interactions": self.user_profile.total_interactions,
            "lifetime_traits": lt.to_dict(),
            "dominant_traits": lt.dominant_traits(0.25),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_session_summary(self) -> str:
        if self._session is None:
            return ""
        p = self._session.profile
        dominant = p.traits.dominant_traits(threshold=0.3)
        if not dominant:
            return f"Early session ({p.interaction_count} messages), no strong patterns yet."
        trait_str = ", ".join(f"{pole} ({t})" for t, pole, _ in dominant[:4])
        return f"Session {p.session_id} ({p.interaction_count} msgs): {trait_str}."
