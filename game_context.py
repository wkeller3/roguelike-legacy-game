# game_context.py
from hero import Hero
from gamemap import GameMap


class GameContext:
    """
    A class to encapsulate all persistent data that needs to be passed
    between different game states.
    """

    def __init__(self, player: Hero = None, game_map: GameMap = None):
        self.player = player
        self.game_map = game_map
