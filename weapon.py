# weapon.py


class Weapon:
    """
    A simple class to hold data about a weapon.
    """

    def __init__(self, name, base_damage, crit_chance, crit_multiplier):
        """
        Args:
            name (str): The name of the weapon.
            base_damage (tuple): A (min, max) tuple for the damage range.
            crit_chance (float): The chance to crit, from 0.0 to 1.0.
            crit_multiplier (float): The multiplier for crit damage (e.g., 1.5 for 150%).
        """
        self.name = name
        self.base_damage = base_damage
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier
