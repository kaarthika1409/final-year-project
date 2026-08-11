from typing import Dict
from backend.app.models import DailyTarget, MealLog

# Default ratio distribution for meal slots
DEFAULT_SLOT_RACK = {
    "breakfast": 0.25,
    "lunch": 0.35,
    "snacks": 0.15,
    "dinner": 0.25,
}

SLOT_ORDER = ["breakfast", "lunch", "snacks", "dinner"]


def recalculate_and_redistribute_daily_target(target: DailyTarget, logs: list[MealLog]) -> DailyTarget:
    """
    Recalculates consumed calories & macros from logs, then adaptively redistributes
    remaining calories across upcoming unconsumed meal slots.
    """
    # Reset consumed counters
    target.consumed_calories = 0.0
    target.consumed_protein = 0.0
    target.consumed_carbs = 0.0
    target.consumed_fat = 0.0

    slot_consumed = {
        "breakfast": 0.0,
        "lunch": 0.0,
        "snacks": 0.0,
        "dinner": 0.0,
    }

    for log in logs:
        target.consumed_calories += log.calories
        target.consumed_protein += log.protein
        target.consumed_carbs += log.carbs
        target.consumed_fat += log.fat

        slot = log.meal_slot.lower()
        if slot in slot_consumed:
            slot_consumed[slot] += log.calories

    # Round totals
    target.consumed_calories = round(target.consumed_calories, 1)
    target.consumed_protein = round(target.consumed_protein, 1)
    target.consumed_carbs = round(target.consumed_carbs, 1)
    target.consumed_fat = round(target.consumed_fat, 1)

    target.breakfast_consumed = round(slot_consumed["breakfast"], 1)
    target.lunch_consumed = round(slot_consumed["lunch"], 1)
    target.snacks_consumed = round(slot_consumed["snacks"], 1)
    target.dinner_consumed = round(slot_consumed["dinner"], 1)

    # Calculate remaining total calories
    remaining_calories = max(0.0, round(target.target_calories - target.consumed_calories, 1))
    target.remaining_calories = remaining_calories

    # Determine which slots have been consumed (consumed > 0)
    unconsumed_slots = [slot for slot in SLOT_ORDER if slot_consumed[slot] == 0.0]

    if not unconsumed_slots:
        # All slots have logged meals: targets are set to what was consumed
        target.breakfast_target = target.breakfast_consumed
        target.lunch_target = target.lunch_consumed
        target.snacks_target = target.snacks_consumed
        target.dinner_target = target.dinner_consumed
    else:
        # Calculate sum of default ratios for unconsumed slots
        unconsumed_ratio_sum = sum(DEFAULT_SLOT_RACK[slot] for slot in unconsumed_slots)

        # Update targets for each slot
        for slot in SLOT_ORDER:
            if slot in unconsumed_slots:
                # Proportional share of remaining calories
                share = (DEFAULT_SLOT_RACK[slot] / unconsumed_ratio_sum) if unconsumed_ratio_sum > 0 else 0
                new_target = round(remaining_calories * share, 1)
                setattr(target, f"{slot}_target", new_target)
            else:
                # For already consumed slots, target remains locked to what was eaten (or original target if logged 0)
                setattr(target, f"{slot}_target", getattr(target, f"{slot}_consumed"))

    return target
