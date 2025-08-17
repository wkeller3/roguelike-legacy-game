# hero.py

import pygame
import constants as C


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

        # --- MODIFIED: Start with base stats instead of randomizing ---
        # We will set these manually after creation
        self.health = 100
        self.max_health = 100
        self.stats = {"Strength": 1, "Dexterity": 1, "Intelligence": 1, "Luck": 1}
        possible_traits = ["Brave", "Cautious", "Avaricious", "Kind", "Clever"]
        self.traits = []  # Traits can be added later in the game

        # --- Equipment ---
        self.equipped_weapon = None  # Will be set after creation

        # --- Combat State ---
        self.is_defending = False  # <-- ADD THIS LINE

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
