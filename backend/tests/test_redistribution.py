"""
Unit Test Suite for Adaptive Redistribution Logic (Stage 3)
------------------------------------------------------------
Validates exact algorithm behavior, proportional redistribution of delta calories,
and guardrails (floor_kcal = 300, max_variance = 20% of daily target).
"""

import pytest
from backend.app.redistribution import apply_adaptive_redistribution


def test_redistribution_under_eaten_breakfast():
    """
    Scenario: User under-eats at breakfast.
    Target: 2000 kcal.
    Planned: breakfast=500, lunch=700, snack=200, dinner=600.
    Actual breakfast: 300 kcal (delta = +200 kcal).
    Expected: Remaining slots (lunch, snack, dinner) increase proportionally.
    """
    target_cals = 2000.0
    initial_targets = {
        "breakfast": 500.0,
        "lunch": 700.0,
        "snack": 300.0,
        "dinner": 500.0,
    }

    updated = apply_adaptive_redistribution(
        target_calories=target_cals,
        current_slot_targets=initial_targets,
        logged_slot="breakfast",
        actual_calories=300.0,
        logged_slots_today=["breakfast"],
    )

    # Remaining weights sum: 0.35 (lunch) + 0.10 (snack) + 0.30 (dinner) = 0.75
    # Lunch share: 0.35/0.75 * 200 = +93.3 -> 793.3
    # Snack share: 0.10/0.75 * 200 = +26.7 -> 326.7
    # Dinner share: 0.30/0.75 * 200 = +80.0 -> 580.0
    assert updated["lunch"] == 793.3
    assert updated["snack"] == 326.7
    assert updated["dinner"] == 580.0


def test_redistribution_over_eaten_lunch_floor_kcal_guardrail():
    """
    Scenario: User over-eats significantly at lunch.
    Target: 2000 kcal.
    Planned: lunch=700, snack=200, dinner=600.
    Actual lunch: 1500 kcal (delta = -800 kcal).
    Guardrail Check: Dinner target must never fall below floor_kcal = 300 kcal.
    """
    target_cals = 2000.0
    initial_targets = {
        "breakfast": 500.0,
        "lunch": 700.0,
        "snack": 200.0,
        "dinner": 600.0,
    }

    updated = apply_adaptive_redistribution(
        target_calories=target_cals,
        current_slot_targets=initial_targets,
        logged_slot="lunch",
        actual_calories=1500.0,
        logged_slots_today=["breakfast", "lunch"],
    )

    # Dinner target is clamped at floor_kcal = 300.0
    assert updated["dinner"] >= 300.0


def test_redistribution_max_variance_guardrail():
    """
    Scenario: Extreme under-eating.
    Guardrail Check: No single slot target swings more than max_variance = 20% of target_calories above planned.
    """
    target_cals = 2000.0  # max_variance = 400 kcal
    initial_targets = {
        "breakfast": 500.0,
        "lunch": 700.0,
        "snack": 200.0,
        "dinner": 600.0,
    }

    # Log 0 cals for breakfast (delta = 500)
    updated = apply_adaptive_redistribution(
        target_calories=target_cals,
        current_slot_targets=initial_targets,
        logged_slot="breakfast",
        actual_calories=0.0,
        logged_slots_today=["breakfast"],
    )

    # Lunch planned = 700. Upper bound = 700 + 400 = 1100.0
    assert updated["lunch"] <= 1100.0
