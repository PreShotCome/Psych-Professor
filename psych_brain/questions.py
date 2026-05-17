"""
Question bank for psychological probing.
Questions are organized by trait and intensity level (0=light, 1=moderate, 2=deep).
Multiple phrasings per slot so the same question never repeats verbatim.
"""
from __future__ import annotations
from .models import SessionProfile, TRAIT_NAMES

# Structured 30-question interview for building a baseline psych profile.
# Each entry: { text, trait, phase }
# Phases: 1=warmup, 2=values/morality, 3=social/interpersonal, 4=power/control, 5=dark reflection
INTERVIEW_QUESTIONS = [
    # One targeted question per trait — calibration run, not a grind
    {
        "phase": 1,
        "phase_name": "Calibration",
        "trait": "moral",
        "text": "If you could do something seriously profitable and completely undetectable — but it would hurt people you'd never meet — would you?",
    },
    {
        "phase": 1,
        "phase_name": "Calibration",
        "trait": "law",
        "text": "Do you follow rules because you believe in them, or because there are consequences for breaking them?",
    },
    {
        "phase": 1,
        "phase_name": "Calibration",
        "trait": "empathy",
        "text": "Tell me about a time you hurt someone — intentionally or not. How did you handle it afterward?",
    },
    {
        "phase": 1,
        "phase_name": "Calibration",
        "trait": "deception",
        "text": "Is there a version of yourself you keep hidden from most people? What does that version think or want?",
    },
    {
        "phase": 1,
        "phase_name": "Calibration",
        "trait": "dominance",
        "text": "When you give someone advice and they ignore it, how do you feel? What do you do?",
    },
    {
        "phase": 2,
        "phase_name": "Depth",
        "trait": "aggression",
        "text": "When someone disrespects you directly, what's your typical response — and what's your ideal response?",
    },
    {
        "phase": 2,
        "phase_name": "Depth",
        "trait": "manipulation",
        "text": "Have you ever deliberately made someone feel a certain way — guilty, grateful, afraid — to get what you wanted?",
    },
    {
        "phase": 2,
        "phase_name": "Depth",
        "trait": "paranoia",
        "text": "Is there anyone in your life you trust completely — who knows everything and couldn't use it against you?",
    },
    {
        "phase": 2,
        "phase_name": "Depth",
        "trait": "impulsivity",
        "text": "Have you ever made a major life decision on impulse — quit a job, ended a relationship, moved somewhere — without much planning? What happened?",
    },
    {
        "phase": 2,
        "phase_name": "Depth",
        "trait": "curiosity",
        "text": "What's the one thing about yourself that you find most difficult to explain to other people?",
    },
]

# [trait][level][phrasing_index]
QUESTION_BANK: dict[str, list[list[str]]] = {
    "moral": [
        [
            "Do you think most people are basically good, or just well-behaved when someone's watching?",
            "Would you say your sense of right and wrong is fixed, or does it shift with the situation?",
            "What's something most people think is wrong that you're not so sure about?",
        ],
        [
            "Have you ever done something you knew was wrong because it was easier than the alternative?",
            "Is there a line you wouldn't cross no matter what? What is it?",
            "Do you think people can actually change, or do they just get better at hiding what they are?",
        ],
        [
            "Is there anyone you think genuinely deserves to suffer?",
            "Have you ever done something you've never told anyone — something that changed how you see yourself?",
            "If you could erase one thing you've done, would you? Or do you own it?",
        ],
    ],
    "aggression": [
        [
            "How do you usually handle it when something doesn't go your way?",
            "Are you someone who confronts problems head-on, or do you let things sit?",
            "What does it actually take to make you angry?",
        ],
        [
            "What's something that makes you lose your patience faster than it should?",
            "Have you ever scared someone — even by accident?",
            "When you're pushed hard enough, what comes out?",
        ],
        [
            "Have you ever hurt someone and genuinely not felt bad about it?",
            "Is there someone you want to see fail?",
            "What's the thing that stops you when part of you wants to do damage?",
        ],
    ],
    "deception": [
        [
            "Are you a good liar?",
            "Do you think a lie that doesn't hurt anyone is still a lie?",
            "How often do you actually say what you mean?",
        ],
        [
            "Have you ever let someone believe something false because the truth was inconvenient for you?",
            "Is there a version of you that you keep hidden from most people?",
            "When someone asks how you're really doing — do you tell them?",
        ],
        [
            "What's the biggest lie you've ever told, and did it work?",
            "Would people like you less if they knew everything about you?",
            "Have you ever steered someone into a decision that was better for you than for them?",
        ],
    ],
    "empathy": [
        [
            "Are you good at reading people?",
            "When someone near you is upset, does it affect how you feel?",
            "Do you usually know what people are feeling, or does it take you a while?",
        ],
        [
            "When someone you don't like is going through something hard, what do you actually feel?",
            "Is there a type of person you just can't bring yourself to care about?",
            "Have you ever realized too late that someone needed you and you weren't there?",
        ],
        [
            "Have you ever felt nothing when you probably should have felt something?",
            "Is there anyone whose pain you're okay with — or maybe even a little satisfied by?",
            "Do you think most suffering is avoidable, or just part of how things are?",
        ],
    ],
    "dominance": [
        [
            "Do you prefer to lead or follow in most situations?",
            "In a group, where do you usually end up?",
            "Do you find it easy to tell people what to do?",
        ],
        [
            "Does it frustrate you when people don't listen to you?",
            "Have you ever taken control of a situation nobody asked you to handle?",
            "Is it hard for you to let someone else be right?",
        ],
        [
            "Do you think most people need someone to tell them what to do?",
            "Have you ever made a decision for someone else without asking them?",
            "What do you do when someone actually challenges your authority?",
        ],
    ],
    "paranoia": [
        [
            "Do you trust people easily, or does that take time?",
            "How much do you pay attention to what people around you are doing?",
            "Do you ever feel like people know more about you than you've shown them?",
        ],
        [
            "Have you ever been right about someone you initially trusted but shouldn't have?",
            "Do you think most people have hidden motives?",
            "How often do you wonder whether someone actually means what they say?",
        ],
        [
            "Is there anyone in your life you trust completely — anyone at all?",
            "When something goes wrong, is your first instinct accident or intention?",
            "Do you ever feel like you're being tested without being told?",
        ],
    ],
    "manipulation": [
        [
            "Are you good at getting what you want from people?",
            "Do you adjust how you come across depending on who you're talking to?",
            "Have you ever talked someone into something they didn't initially want?",
        ],
        [
            "Do you know what makes the people around you tick?",
            "Is there a difference between persuasion and manipulation, to you?",
            "Have you ever used someone's weakness to get something from them?",
        ],
        [
            "Have you ever made someone feel a certain way on purpose, just to see if you could?",
            "Do you ever plan conversations in advance — what you'll say, how they'll react?",
            "What do you do when someone figures out what you're doing?",
        ],
    ],
    "impulsivity": [
        [
            "Do you tend to think things through, or go with your gut?",
            "How often do you do something without really planning it first?",
            "Are you someone who takes risks?",
        ],
        [
            "Have you ever done something in the moment that you regretted almost immediately?",
            "When you want something, how long can you actually wait for it?",
            "What's the most impulsive thing you've done recently?",
        ],
        [
            "Have you ever blown something up — a relationship, a situation — just to see what happened?",
            "Is there a version of you that comes out when you stop thinking? What does it do?",
            "Do you ever do things specifically because you're not supposed to?",
        ],
    ],
    "curiosity": [
        [
            "Are you someone who needs to understand how things work?",
            "Do you read between the lines, or take things at face value?",
            "What's something you've been turning over in your head lately?",
        ],
        [
            "Is there anything you know you probably shouldn't have looked into?",
            "Do you ever ask questions you already know the answer to, just to see what someone says?",
            "What's the most interesting thing you've learned about a person that changed how you saw them?",
        ],
        [
            "Is there a question you're afraid to know the answer to?",
            "Have you ever kept digging after everyone told you to leave something alone?",
            "What do you do when you find out something about someone they didn't want you to know?",
        ],
    ],
    "law": [
        [
            "Do you follow rules because you believe in them, or because there are consequences?",
            "Are you the type who asks permission or forgiveness?",
            "Do you think the rules apply equally to everyone?",
        ],
        [
            "Have you ever broken a rule you thought was unjust? Did it feel right?",
            "What's a rule you think is stupid but follow anyway?",
            "Do you think order is worth what it costs to maintain?",
        ],
        [
            "Do you think society's laws reflect actual morality, or just whoever has power?",
            "Is there a situation where chaos is genuinely better than order?",
            "Have you ever decided the rules simply didn't apply to you?",
        ],
    ],
}


def select_questions(session: SessionProfile, interaction_count: int) -> list[str]:
    """
    Pick 2 probing questions targeting the player's least-mapped trait areas.
    Intensity scales with interaction count. Cycles through phrasings to avoid repeats.
    """
    if interaction_count < 4:
        level = 0
    elif interaction_count < 10:
        level = 1
    else:
        level = 2

    # Sort traits by how little signal we have on them (weakest first = most unexplored)
    trait_values = session.traits.to_dict()
    sorted_traits = sorted(
        [t for t in TRAIT_NAMES if t in QUESTION_BANK],
        key=lambda t: abs(trait_values.get(t, 0.0)),
    )

    selected = []
    for trait in sorted_traits:
        phrasings = QUESTION_BANK[trait][level]
        # Cycle through phrasings based on how many times we've been in this level
        idx = (interaction_count // max(1, len(phrasings))) % len(phrasings)
        selected.append(phrasings[idx])
        if len(selected) >= 2:
            break

    return selected
