# game_context.py
from hero import Hero
from gamemap import GameMap


class GameContext:
    """
    A class to encapsulate all persistent data that needs to be passed
    between different game states.
    """

    def __init__(self):
        self.player: Hero = None
        self.game_map: GameMap = None

        # These are used for transitions to/from the overworld
        self.entry_direction = None
        self.exit_to_overworld_from = None
        self.overworld_entry_direction = None

        # This is used to pass the active enemy into combat
        self.active_enemy = None
