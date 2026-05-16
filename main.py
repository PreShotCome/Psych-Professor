#!/usr/bin/env python3
"""
Interactive CLI for testing the PsychBrain system.

Usage:
    python main.py
    python main.py --user player1 --name "Alex" --debug
    python main.py --user player1 --session-id mysession
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def print_divider(char: str = "─", width: int = 60) -> None:
    print(char * width)


def print_analysis(analysis: dict) -> None:
    print_divider("·")
    print(f"  [Signals this turn]")
    sigs = {k: round(v, 2) for k, v in analysis["signals_this_turn"].items() if abs(v) >= 0.15}
    if sigs:
        for k, v in sigs.items():
            bar = "█" * int(abs(v) * 10)
            direction = "+" if v > 0 else "-"
            print(f"    {k:<14} {direction}{bar} ({v:+.2f})  — {analysis['signal_notes'][:60]}")
    else:
        print(f"    (no strong signals)  {analysis['signal_notes'][:80]}")

    print(f"\n  [Session #{analysis['interaction_count']}  |  divergence from lifetime: {analysis['divergence']:.2f}]")

    if analysis["session_dominant"]:
        traits = ", ".join(f"{pole}({v:.2f})" for _, pole, v in analysis["session_dominant"])
        print(f"  Session profile: {traits}")

    if analysis["archetype"]:
        print(f"  Lifetime archetype: {analysis['archetype']}")
    print_divider("·")


def run_cli(user_id: str, display_name: str, debug: bool, session_id: str | None) -> None:
    from psych_brain import PsychBrain

    brain = PsychBrain(
        user_id=user_id,
        display_name=display_name,
        npc_persona="a cryptic tavern keeper who seems to know everyone's secrets",
        model="claude-opus-4-7",
    )

    sid = brain.start_session(session_id=session_id)
    print_divider("═")
    print(f"  PSYCH BRAIN  |  Player: {display_name}  |  Session: {sid}")
    lifetime = brain.user_profile.total_interactions
    print(f"  Lifetime interactions: {lifetime}  |  Sessions: {brain.user_profile.session_count - 1} prior")
    if brain.user_profile.archetype:
        print(f"  Known archetype: {brain.user_profile.archetype}")
    print_divider("═")
    print("  Commands: /profile  /session  /quit")
    print_divider("═")
    print()

    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not user_input:
                continue

            if user_input.lower() in ("/quit", "/exit", "/q"):
                break

            if user_input.lower() == "/profile":
                summary = brain.get_profile_summary()
                print(json.dumps(summary, indent=2, default=str))
                continue

            if user_input.lower() == "/session":
                snap = brain.get_session_snapshot()
                print(json.dumps(snap, indent=2, default=str))
                continue

            result = brain.process(user_input, return_analysis=True)

            if isinstance(result, dict):
                print(f"\nNPC: {result['response']}\n")
                if debug:
                    print_analysis(result)
                    print()
            else:
                print(f"\nNPC: {result}\n")

    finally:
        print("\nEnding session...")
        brain.end_session()
        summary = brain.get_profile_summary()
        print_divider("═")
        print(f"  Session complete. Archetype: {summary['archetype']}")
        print(f"  Total interactions: {summary['total_interactions']}")
        dominant = summary["dominant_traits"]
        if dominant:
            print(f"  Lifetime dominant: " + ", ".join(f"{p}({v:.2f})" for _, p, v in dominant))
        print_divider("═")


def main() -> None:
    parser = argparse.ArgumentParser(description="PsychBrain interactive test CLI")
    parser.add_argument("--user", default="player_001", help="User/player ID")
    parser.add_argument("--name", default=None, help="Display name (defaults to user ID)")
    parser.add_argument("--debug", action="store_true", help="Show psychological analysis per turn")
    parser.add_argument("--session-id", default=None, help="Override session ID")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set. Add it to a .env file or export it.")
        sys.exit(1)

    run_cli(
        user_id=args.user,
        display_name=args.name or args.user,
        debug=args.debug,
        session_id=args.session_id,
    )


if __name__ == "__main__":
    main()
