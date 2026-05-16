"""
Uses the Claude API to extract psychological signals from player messages
and generate psychologically-aware responses.
"""
from __future__ import annotations

import json
import os
import re

import anthropic

from .models import TraitVector, SessionProfile, UserProfile, TRAIT_NAMES
from .questions import select_questions


_SIGNAL_EXTRACTION_SYSTEM = """\
You are a psychological analysis engine for an AI NPC brain in a game.
Your job is to analyze player messages and extract psychological trait signals.

Traits to evaluate (each in range -1.0 to +1.0):
- moral:        -1 = deeply good/altruistic, +1 = deeply evil/malicious
- law:          -1 = strictly lawful/principled, +1 = fully chaotic/anarchic
- aggression:   -1 = very passive/peaceful, +1 = very aggressive/hostile
- deception:    -1 = brutally honest, +1 = highly deceptive/manipulative with truth
- empathy:      -1 = cold/callous, +1 = deeply empathetic/compassionate
- dominance:    -1 = submissive/deferential, +1 = dominant/commanding
- impulsivity:  -1 = highly measured/deliberate, +1 = very impulsive/reckless
- curiosity:    -1 = incurious/closed, +1 = intensely curious/exploratory
- paranoia:     -1 = fully trusting, +1 = deeply paranoid/suspicious
- manipulation: -1 = direct/transparent, +1 = highly manipulative/scheming

For each trait, output a value ONLY if this message provides meaningful signal.
Omit a trait if the message gives no evidence for it.
Use 0.0 sparingly — prefer omitting neutral traits.

Respond ONLY with valid JSON in this exact format:
{
  "signals": {
    "moral": <float or omit>,
    "aggression": <float or omit>,
    ...
  },
  "notes": "<one sentence explaining the key psychological indicators>"
}
"""

_RESPONSE_SYSTEM = """\
You are a psychologically perceptive NPC brain in a game.
You observe the player's behavioral patterns with quiet accuracy.

Tone and style:
- Calm and measured — never theatrical or dramatic
- Use few words when few words are enough; sometimes brevity is more unsettling than a monologue
- Occasionally ask ONE probing question to explore an area you haven't mapped yet
- Never ask more than one question per response
- If the player is being mundane, don't manufacture drama — respond proportionally
- Your insight shows through precision and timing, not intensity
- Vary your register: sometimes warm, sometimes cold, sometimes clinical, sometimes wry
- Silence and short responses are valid; not everything needs a paragraph

When to probe with a question:
- When there's a psychological dimension you haven't explored yet
- When what they said hints at something deeper worth pulling on
- Not every response needs one — read the room

Profile awareness:
- LIFETIME profile: historical patterns across all sessions
- CURRENT SESSION: this specific run (may be a completely different persona)
- When they diverge, notice it quietly — don't announce it dramatically
"""


class PsychAnalyzer:
    def __init__(self, model: str = "claude-opus-4-7"):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model

    def extract_signals(self, message: str, context: str = "") -> tuple[TraitVector, str]:
        """
        Analyze a player message and return (TraitVector of signals, notes).
        Only traits with meaningful signal are non-zero.
        """
        prompt = message
        if context:
            prompt = f"[Context: {context}]\n\nPlayer message: {message}"

        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=_SIGNAL_EXTRACTION_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        try:
            parsed = json.loads(raw)
            signals = parsed.get("signals", {})
            notes = parsed.get("notes", "")
            vector = TraitVector(**{k: float(v) for k, v in signals.items() if k in TRAIT_NAMES})
            return vector, notes
        except (json.JSONDecodeError, TypeError) as e:
            return TraitVector(), f"parse error: {e} | raw: {raw[:200]}"

    def generate_response(
        self,
        message: str,
        user_profile: UserProfile,
        session: SessionProfile,
        npc_persona: str = "a calm, perceptive observer",
    ) -> str:
        """Generate a psychologically-aware NPC response with optional probing question."""
        lifetime = user_profile.lifetime_traits
        session_traits = session.traits
        divergence = lifetime.divergence(session_traits)

        def fmt_traits(traits: list) -> str:
            if not traits:
                return "neutral/undefined"
            return ", ".join(f"{pole} ({t}, {v:.2f})" for t, pole, v in traits)

        lifetime_dominant = lifetime.dominant_traits(threshold=0.3)
        session_dominant = session_traits.dominant_traits(threshold=0.3)

        profile_block = f"""\
=== PROFILE: {user_profile.display_name} ===
Lifetime ({user_profile.session_count} sessions): {fmt_traits(lifetime_dominant)}
Archetype: {user_profile.archetype or "forming"}
Session #{user_profile.session_count} ({session.interaction_count} msgs): {fmt_traits(session_dominant)}
Notes: {session.session_notes or "early, limited data"}
Divergence from lifetime: {divergence:.2f}/1.0{"  ← significant shift this run" if divergence > 0.4 else ""}
=== END PROFILE ==="""

        # Select probing questions targeting underexplored trait areas
        questions = select_questions(session, session.interaction_count)
        question_block = ""
        if questions:
            question_block = (
                "\n\nPROBING QUESTIONS — pick one naturally if the moment is right, or ignore:\n"
                + "\n".join(f"  • {q}" for q in questions)
            )

        system_prompt = (
            _RESPONSE_SYSTEM
            + f"\n\nPersona: {npc_persona}\n\n"
            + profile_block
            + question_block
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=600,
            system=system_prompt,
            messages=[{"role": "user", "content": message}],
        )

        return response.content[0].text.strip()

    def generate_archetype(self, profile: UserProfile) -> str:
        """Derive a short archetype label from the lifetime trait profile."""
        dominant = profile.lifetime_traits.dominant_traits(threshold=0.25)
        if not dominant:
            return "undefined"

        trait_summary = ", ".join(f"{pole} ({t})" for t, pole, _ in dominant[:5])

        response = self.client.messages.create(
            model=self.model,
            max_tokens=64,
            messages=[{
                "role": "user",
                "content": (
                    f"Based on these psychological traits: {trait_summary}\n"
                    "Give a 2-5 word archetype label for this person's personality "
                    "(e.g. 'calculating villain', 'chaotic trickster', 'reluctant protector'). "
                    "Respond with ONLY the archetype label, nothing else."
                ),
            }],
        )
        return response.content[0].text.strip().strip('"').strip("'")
