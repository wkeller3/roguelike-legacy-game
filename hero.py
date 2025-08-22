# hero.py

import pygame
import constants as C
from factories import ITEM_TEMPLATES


# Make the Hero class a Pygame Sprite for 2D game object functionality.
class Hero(pygame.sprite.Sprite):
    """
    Represents the hero, now as a movable sprite.
    Inherits from pygame.sprite.Sprite.
    """

    def __init__(self, first_name, family_name, pos_x, pos_y):
        """
        The constructor is updated to handle sprite properties.
        pos_x and pos_y are the starting coordinates for the hero.
        """
        # This line is essential - it runs the constructor of the parent Sprite class.
        super().__init__()

        # --- Visual Representation (The Sprite's "image" and "rect") ---
        # Instead of loading an image file, we create a simple square surface.
        self.image = pygame.Surface((32, 32))  # A 32x32 pixel square
        self.image.fill(C.BLUE)  # Hero is blue

        # --- To use a real image file later ---
        # 1. Make sure your image (e.g., 'hero.png') is in the same folder.
        # 2. Comment out the two lines above.
        # 3. Uncomment the line below.
        # self.image = pygame.image.load('hero.png').convert_alpha()

        # A "rect" is a rectangle that represents the sprite's position and size.
        # It's essential for movement, drawing, and collision detection.
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)  # Set the starting position

        # --- Game Data (Same as before) ---
        self.first_name = first_name
        self.family_name = family_name

        # --- Start with base stats instead of randomizing ---
        # We will set these manually after creation
        self.health = C.PLAYER_STARTING_HEALTH
        self.max_health = C.PLAYER_STARTING_HEALTH
        self.gold = 0
        self.inventory = []
        self.stats = {"Strength": 1, "Dexterity": 1, "Intelligence": 1, "Luck": 1}
        possible_traits = ["Brave", "Cautious", "Avaricious", "Kind", "Clever"]
        self.traits = []  # Traits can be added later in the game
        self.experience = 0

        # --- Equipment ---
        self.equipped_weapon = None  # Will be set after creation

        # --- Combat State ---
        self.is_defending = False

    def move(self, dx, dy, screen_width, screen_height):
        """
        Moves the hero by a given amount (dx, dy) and keeps them on screen.
        """
        self.rect.x += dx
        self.rect.y += dy

        # Boundary checking to prevent the hero from leaving the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

    def to_dict(self, current_room_coords=None):
        """Converts the hero's state to a dictionary for saving."""
        weapon_id = next(
            (
                w_id
                for w_id, w_obj in ITEM_TEMPLATES.items()
                if w_obj.name == self.equipped_weapon.name
            ),
            None,
        )
        return {
            "first_name": self.first_name,
            "family_name": self.family_name,
            "health": self.health,
            "gold": self.gold,
            "experience": self.experience,
            "inventory": [item.item_id for item in self.inventory],
            "stats": self.stats,
            "equipped_weapon_id": weapon_id,
            "position": {
                "pos_in_room": self.rect.center,
                "room_coords": current_room_coords,
            },
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Hero instance from a dictionary of saved data."""
        player = cls(
            first_name=data["first_name"],
            family_name=data["family_name"],
            pos_x=data["position"]["pos_in_room"][0],
            pos_y=data["position"]["pos_in_room"][1],
        )
        player.health = data["health"]
        player.gold = data["gold"]
        player.experience = data["experience"]
        # --- Recreate the inventory from saved IDs ---
        player.inventory = []
        if "inventory" in data:
            for item_id in data["inventory"]:
                player.inventory.append(ITEM_TEMPLATES[item_id])
        player.stats = data["stats"]
        if data["equipped_weapon_id"]:
            player.equipped_weapon = ITEM_TEMPLATES[data["equipped_weapon_id"]]
        return player
