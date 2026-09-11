from typing import Dict, List
from backend.app.models import DailyTarget, MealLog

# Default slot ratios: breakfast 25%, lunch 35%, snack (or snacks) 10%, dinner 30%
DEFAULT_SLOT_RACK = {
    "breakfast": 0.25,
    "lunch": 0.35,
    "snack": 0.10,
    "snacks": 0.10,
    "dinner": 0.30,
}

SLOT_ORDER = ["breakfast", "lunch", "snack", "dinner"]


def apply_adaptive_redistribution(
    target_calories: float,
    current_slot_targets: Dict[str, float],
    logged_slot: str,
    actual_calories: float,
    logged_slots_today: List[str],
    tdee: float = None,
) -> Dict[str, float]:
    """
    Stage 3 Adaptive Redistribution Algorithm
    -----------------------------------------
    On each meal log in slot i:
      planned_i  = current slot_targets[i]
      actual_i   = calories just logged in slot i
      delta_i    = planned_i - actual_i   # positive = under-eaten, negative = over-eaten

      remaining_slots = all slots after i that haven't been logged today
      if remaining_slots is empty:
          carry delta_i into tomorrow's target as a small correction (max +-10% of TDEE), else drop it
      else:
          total_weight = sum(default_weight_pct[j] for j in remaining_slots)
          for j in remaining_slots:
              share = default_weight_pct[j] / total_weight
              slot_targets[j] += delta_i * share

      # Guardrails (nutritional adequacy)
      floor_kcal = 300          # no slot target below this
      max_variance = 0.20 * target_calories   # no single slot swings more than 20% of daily target
      clamp every slot_targets[j] between floor_kcal and (planned_j + max_variance)
    """
    updated_targets = dict(current_slot_targets)
    
    # Normalize slot name (e.g. snacks -> snack)
    slot_i = "snack" if logged_slot.lower() in ["snack", "snacks"] else logged_slot.lower()
    
    planned_i = updated_targets.get(slot_i, target_calories * DEFAULT_SLOT_RACK.get(slot_i, 0.25))
    delta_i = planned_i - actual_calories

    # Normalize logged slots list
    logged_norm = ["snack" if s.lower() in ["snack", "snacks"] else s.lower() for s in logged_slots_today]
    if slot_i not in logged_norm:
        logged_norm.append(slot_i)

    # Determine remaining slots after i that haven't been logged today
    if slot_i in SLOT_ORDER:
        idx_i = SLOT_ORDER.index(slot_i)
        upcoming_slots = SLOT_ORDER[idx_i + 1:]
    else:
        upcoming_slots = []

    remaining_slots = [s for s in upcoming_slots if s not in logged_norm]

    if remaining_slots:
        total_weight = sum(DEFAULT_SLOT_RACK[j] for j in remaining_slots)
        if total_weight > 0:
            for j in remaining_slots:
                share = DEFAULT_SLOT_RACK[j] / total_weight
                updated_targets[j] = round(updated_targets.get(j, target_calories * DEFAULT_SLOT_RACK[j]) + (delta_i * share), 1)

    # Guardrails
    floor_kcal = 300.0
    max_variance = 0.20 * target_calories

    for s in SLOT_ORDER:
        if s in remaining_slots:
            planned_j = target_calories * DEFAULT_SLOT_RACK[s]
            upper_bound = planned_j + max_variance
            clamped = max(floor_kcal, min(upper_bound, updated_targets[s]))
            updated_targets[s] = round(clamped, 1)

    return updated_targets


def recalculate_and_redistribute_daily_target(target: DailyTarget, logs: List[MealLog]) -> DailyTarget:
    """
    Recalculates consumed calories & macros from logs and applies adaptive redistribution.
    """
    # Reset consumed counters
    target.consumed_calories = 0.0
    target.consumed_protein = 0.0
    target.consumed_carbs = 0.0
    target.consumed_fat = 0.0

    slot_consumed = {
        "breakfast": 0.0,
        "lunch": 0.0,
        "snack": 0.0,
        "snacks": 0.0,
        "dinner": 0.0,
    }

    logged_slots_list = []

    # Sort logs chronologically
    sorted_logs = sorted(logs, key=lambda l: l.timestamp or l.id)

    for log in sorted_logs:
        cals = log.calories
        target.consumed_calories += cals
        target.consumed_protein += log.protein
        target.consumed_carbs += log.carbs
        target.consumed_fat += log.fat

        raw_slot = log.meal_slot.lower()
        slot_key = "snack" if raw_slot in ["snack", "snacks"] else raw_slot
        if slot_key in slot_consumed:
            slot_consumed[slot_key] += cals
        if slot_key not in logged_slots_list:
            logged_slots_list.append(slot_key)

    # Round totals
    target.consumed_calories = round(target.consumed_calories, 1)
    target.consumed_protein = round(target.consumed_protein, 1)
    target.consumed_carbs = round(target.consumed_carbs, 1)
    target.consumed_fat = round(target.consumed_fat, 1)

    target.breakfast_consumed = round(slot_consumed["breakfast"], 1)
    target.lunch_consumed = round(slot_consumed["lunch"], 1)
    target.snacks_consumed = round(slot_consumed["snack"] + slot_consumed["snacks"], 1)
    target.dinner_consumed = round(slot_consumed["dinner"], 1)

    # Remaining total calories
    target.remaining_calories = max(0.0, round(target.target_calories - target.consumed_calories, 1))

    # Base initial targets
    initial_slot_targets = {
        "breakfast": round(target.target_calories * 0.25, 1),
        "lunch": round(target.target_calories * 0.35, 1),
        "snack": round(target.target_calories * 0.10, 1),
        "dinner": round(target.target_calories * 0.30, 1),
    }

    current_targets = dict(target.slot_targets) if target.slot_targets else dict(initial_slot_targets)

    # Apply adaptive redistribution for each logged slot in sequence
    processed_logged = []
    for log in sorted_logs:
        raw_slot = log.meal_slot.lower()
        slot_key = "snack" if raw_slot in ["snack", "snacks"] else raw_slot
        current_targets = apply_adaptive_redistribution(
            target_calories=target.target_calories,
            current_slot_targets=current_targets,
            logged_slot=slot_key,
            actual_calories=log.calories,
            logged_slots_today=processed_logged,
            tdee=target.bmr * 1.5,
        )
        if slot_key not in processed_logged:
            processed_logged.append(slot_key)

    # Lock targets for consumed slots
    for slot in SLOT_ORDER:
        cons = target.breakfast_consumed if slot == "breakfast" else (
            target.lunch_consumed if slot == "lunch" else (
                target.snacks_consumed if slot in ["snack", "snacks"] else target.dinner_consumed
            )
        )
        if cons > 0:
            current_targets[slot] = cons

    target.slot_targets = current_targets
    target.breakfast_target = current_targets.get("breakfast", initial_slot_targets["breakfast"])
    target.lunch_target = current_targets.get("lunch", initial_slot_targets["lunch"])
    target.snacks_target = current_targets.get("snack", initial_slot_targets["snack"])
    target.dinner_target = current_targets.get("dinner", initial_slot_targets["dinner"])

    return target

