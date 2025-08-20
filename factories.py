# factories.py
import json
from enemy import Enemy
from item import Item
from weapon import Weapon

# --- Load all weapon, enemy, and item data at startup ---
with open("weapons.json", "r") as f:
    WEAPON_TEMPLATES_DATA = json.load(f)

with open("enemies.json", "r") as f:
    ENEMY_TEMPLATES = json.load(f)

with open("items.json", "r") as f:
    ITEM_TEMPLATES_DATA = json.load(f)

with open("vendors.json", "r") as f:
    VENDOR_INVENTORIES = json.load(f)

# Create a dictionary of Weapon objects, ready to be used
WEAPON_TEMPLATES = {
    w_id: Weapon(
        name=w_data["name"],
        base_damage=tuple(w_data["base_damage"]),
        crit_chance=w_data["crit_chance"],
        crit_multiplier=w_data["crit_multiplier"],
    )
    for w_id, w_data in WEAPON_TEMPLATES_DATA.items()
}

ITEM_TEMPLATES = {
    i_id: Item(
        item_id=i_id,
        name=i_data["name"],
        value=i_data["value"],
    )
    for i_id, i_data in ITEM_TEMPLATES_DATA.items()
}


def create_enemy(enemy_name, x, y):
    """
    Creates an instance of an enemy using a template from the loaded data.

    Args:
        enemy_name (str): The key for the enemy in the ENEMY_TEMPLATES dict (e.g., "goblin").
        x (int): The x-coordinate to spawn the enemy at.
        y (int): The y-coordinate to spawn the enemy at.

    Returns:
        Enemy: An instance of the Enemy class, configured with the template data.
    """
    template = ENEMY_TEMPLATES[enemy_name]
    weapon_id = template["weapon"]
    weapon = WEAPON_TEMPLATES[weapon_id]
    return Enemy(x, y, template, weapon)


def get_available_enemy_types():
    """Returns a list of all enemy names that can be spawned."""
    return list(ENEMY_TEMPLATES.keys())
