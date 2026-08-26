"""
Spaced Repetition Engine (Leitner / SuperMemo-2) for Formula Vault
"""
from typing import Dict, Any, List
from database.db import get_formula_vault, update_formula_review


def get_due_formula_cards() -> List[Dict[str, Any]]:
    """Retrieves all formula cards currently due for review."""
    return get_formula_vault(due_only=True)


def process_formula_feedback(topic_id: str, feedback_type: str) -> None:
    """
    Processes candidate review feedback:
    - 'forgot' -> score 0
    - 'hesitated' -> score 1
    - 'easy' -> score 2
    """
    scores = {"forgot": 0, "hesitated": 1, "easy": 2}
    score = scores.get(feedback_type, 1)
    update_formula_review(topic_id, score)


def get_formula_deck_statistics() -> Dict[str, Any]:
    """Provides summary statistics for the formula vault deck."""
    deck = get_formula_vault(due_only=False)
    total = len(deck)
    learning = len([c for c in deck if c["mastery_status"] == "Learning"])
    reviewing = len([c for c in deck if c["mastery_status"] == "Reviewing"])
    mastered = len([c for c in deck if c["mastery_status"] == "Mastered"])
    due_today = len(get_formula_vault(due_only=True))

    return {
        "total_cards": total,
        "learning": learning,
        "reviewing": reviewing,
        "mastered": mastered,
        "due_today": due_today,
        "mastery_rate": round((mastered / total * 100), 1) if total > 0 else 0.0
    }
