# factories.py
import json
from enemy import Enemy
from item import Item, Weapon, Consumable

# --- Load all weapon, enemy, and item data at startup ---
with open("items.json", "r") as f:
    ITEM_TEMPLATES_DATA = json.load(f)

with open("enemies.json", "r") as f:
    ENEMY_TEMPLATES = json.load(f)

with open("vendors.json", "r") as f:
    VENDOR_INVENTORIES = json.load(f)

# Create a dictionary of Weapon objects, ready to be used
ITEM_TEMPLATES = {}
for item_id, item_data in ITEM_TEMPLATES_DATA.items():
    item_type = item_data.get("type", "junk")
    if item_type == "weapon":
        ITEM_TEMPLATES[item_id] = Weapon(
            item_id=item_id,
            name=item_data["name"],
            value=item_data["value"],
            base_damage=tuple(item_data["base_damage"]),
            crit_chance=item_data["crit_chance"],
            crit_multiplier=item_data["crit_multiplier"],
        )
    elif item_type == "consumable":
        ITEM_TEMPLATES[item_id] = Consumable(
            item_id=item_id,
            name=item_data["name"],
            value=item_data["value"],
            effect=item_data["effect"],
        )
    else:  # Default to a basic item
        ITEM_TEMPLATES[item_id] = Item(
            item_id=item_id, name=item_data["name"], value=item_data["value"]
        )


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
    weapon = ITEM_TEMPLATES[weapon_id]
    return Enemy(x, y, template, weapon)


def get_available_enemy_types():
    """Returns a list of all enemy names that can be spawned."""
    return list(ENEMY_TEMPLATES.keys())
