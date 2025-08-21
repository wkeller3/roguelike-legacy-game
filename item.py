# item.py


class Item:
    """A base class for all items."""

    def __init__(self, item_id, name, value):
        self.item_id = item_id
        self.name = name
        self.value = value


class Weapon(Item):
    """A subclass of Item for equippable weapons."""

    def __init__(self, item_id, name, value, base_damage, crit_chance, crit_multiplier):
        super().__init__(item_id, name, value)
        self.base_damage = base_damage
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier


class Consumable(Item):
    """A subclass of Item for usable items like potions."""

    def __init__(self, item_id, name, value, effect):
        super().__init__(item_id, name, value)
        self.effect = effect

    def use(self, target):
        """Applies the item's effect to a target."""
        if self.effect.get("heal_amount"):
            target.health = min(
                target.max_health, target.health + self.effect["heal_amount"]
            )
            print(f"Used {self.name}, healed for {self.effect['heal_amount']} HP.")
            return True  # Indicates the item was successfully used
        return False
