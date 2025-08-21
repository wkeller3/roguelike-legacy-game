# weapon.py
from object import Object


class Weapon(Object):
    """
    A simple class to hold data about a weapon.
    """

    def __init__(self, name, base_damage, crit_chance, crit_multiplier, value=0):
        """
        Args:
            name (str): The name of the weapon.
            base_damage (tuple): A (min, max) tuple for the damage range.
            crit_chance (float): The chance to crit, from 0.0 to 1.0.
            crit_multiplier (float): The multiplier for crit damage (e.g., 1.5 for 150%).
        """
        super().__init__(
            object_id=name.lower().replace(" ", "_"),  # Use name as ID, formatted
            name=name,
            value=value,
            object_type="weapon",  # Specify the type as 'weapon'
        )
        self.base_damage = base_damage
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier
