# factories.py
import json
from item import Item, Weapon, Consumable
from gene import Gene, StatGene, TraitGene, CosmeticGene

# --- Load all weapon, enemy, and item data at startup ---
with open("items.json", "r") as f:
    ITEM_TEMPLATES_DATA = json.load(f)

with open("enemies.json", "r") as f:
    ENEMY_TEMPLATES = json.load(f)

with open("vendors.json", "r") as f:
    VENDOR_INVENTORIES = json.load(f)

with open("genetics.json", "r") as f:
    GENE_TEMPLATES_DATA = json.load(f)

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

# --- Create a dictionary of Gene objects ---
GENE_TEMPLATES = {}
for gene_id, gene_data in GENE_TEMPLATES_DATA.items():
    gene_type = gene_data.get("type")
    if gene_type == "stat":
        GENE_TEMPLATES[gene_id] = StatGene(
            gene_id=gene_id,
            name=gene_data["name"],
            gene_type=gene_type,
            value=0,  # Base value is 0, will be set per character
            min_value=gene_data["min_value"],
            max_value=gene_data["max_value"],
        )
    elif gene_type == "trait":
        GENE_TEMPLATES[gene_id] = TraitGene(
            gene_id=gene_id,
            name=gene_data["name"],
            gene_type=gene_type,
            description=gene_data["description"],
            effects=gene_data["effects"],
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
    from enemy import Enemy

    template = ENEMY_TEMPLATES[enemy_name]
    weapon_id = template["weapon"]
    weapon = ITEM_TEMPLATES[weapon_id]
    return Enemy(x, y, template, weapon)


def get_available_enemy_types():
    """Returns a list of all enemy names that can be spawned."""
    return list(ENEMY_TEMPLATES.keys())
