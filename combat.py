# combat.py
import random


def resolve_attack(attacker, defender, attack_type="normal"):
    """
    Calculates the outcome of a single attack, now with different attack types.
    Returns a dictionary with the results.
    """
    hit_modifier = 0
    damage_modifier = 1.0
    message_prefix = ""

    # Apply modifiers based on the attack type
    if attack_type == "power":
        hit_modifier = -20  # Power attacks are 20% less likely to hit
        damage_modifier = 1.5  # Power attacks deal 150% damage
        message_prefix = "A powerful blow! "
    # --- Logic for the enemy's special attack ---
    elif attack_type == "vicious_bite":
        hit_modifier = -10  # Still a bit less accurate than a normal hit
        damage_modifier = 2.5  # But deals massive damage
        message_prefix = "Vicious Bite! "

    # 1. Calculate Hit Chance
    hit_chance = (
        90
        + (attacker.stats["Dexterity"] * 2)
        - (defender.stats["Dexterity"])
        + hit_modifier
    )
    if random.randint(1, 100) > hit_chance:
        return {
            "type": "miss",
            "damage": 0,
            "message": f"{attacker.first_name if hasattr(attacker, 'first_name') else 'Enemy'} missed!",
        }

    # 2. Calculate Base Damage
    min_dmg, max_dmg = attacker.equipped_weapon.base_damage
    base_damage = random.randint(min_dmg, max_dmg)

    # 3. Add Strength Bonus
    strength_bonus = attacker.stats["Strength"] // 2
    total_damage = base_damage + strength_bonus

    # Apply the damage modifier for power attacks
    total_damage = int(total_damage * damage_modifier)

    # 4. Calculate Critical Hit (Power attacks can't also be crits for now, to keep it simple)
    if attack_type == "normal":
        crit_roll_chance = (
            attacker.equipped_weapon.crit_chance * 100 + attacker.stats.get("Luck", 0)
        )
        if random.randint(1, 100) <= crit_roll_chance:
            total_damage = int(total_damage * attacker.equipped_weapon.crit_multiplier)
            return {
                "type": "crit",
                "damage": total_damage,
                "message": f"Critical Hit! {attacker.first_name if hasattr(attacker, 'first_name') else 'Enemy'} deals {total_damage} damage!",
            }

    # 5. Return a normal (or power) hit
    return {
        "type": "hit",
        "damage": total_damage,
        "message": f"{message_prefix}{attacker.first_name if hasattr(attacker, 'first_name') else 'Enemy'} deals {total_damage} damage!",
    }
