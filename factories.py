# factories.py
import json
from enemy import Enemy

# --- Load all enemy data from the JSON file at startup ---
with open("enemies.json", "r") as f:
    ENEMY_TEMPLATES = json.load(f)


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
    return Enemy(x, y, template)


def get_available_enemy_types():
    """Returns a list of all enemy names that can be spawned."""
    return list(ENEMY_TEMPLATES.keys())
