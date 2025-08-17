# factories.py
from enemy import Goblin, Orc


# The factories are now very simple: they just create an instance of the class.
def goblin(x, y):
    """Creates a Goblin at a given position."""
    return Goblin(x, y)


def orc(x, y):
    """Creates an Orc at a given position."""
    return Orc(x, y)


# A dictionary to easily access all our enemy factory functions.
# This makes it easy to randomly select an enemy to spawn.
enemy_factories = {
    "goblin": goblin,
    "orc": orc,
}
