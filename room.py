# room.py
import pygame
import random
from factories import enemy_factories  # Import our new enemy factory


class Room:
    """
    A class that represents a single room in the game. It holds and manages
    all the sprites and data for that specific area.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # These sprite groups will contain all the objects in this room
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.loot = pygame.sprite.Group()  # For later use

        # Populate the room with some enemies
        self.spawn_enemies()

    def add_sprite(self, sprite):
        """A helper method to add a sprite to the all_sprites group."""
        self.all_sprites.add(sprite)

    def spawn_enemies(self):
        """Create enemies and add them to the appropriate groups."""

        # We can create a specific number of enemies here.
        # Later, this number can be randomized.
        num_enemies = random.randint(1, 3)

        # --- Randomly select which type of enemy to spawn ---
        available_enemy_types = list(enemy_factories.keys())

        for _ in range(num_enemies):
            x = random.randint(self.width // 2, self.width - 50)
            y = random.randint(50, self.height - 50)

            # Choose a random enemy type (e.g., "goblin" or "orc")
            enemy_type_key = random.choice(available_enemy_types)

            # Get the correct factory function from the dictionary
            enemy_factory = enemy_factories[enemy_type_key]

            # Call the factory to create the enemy instance
            enemy = enemy_factory(x=x, y=y)

            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

    def update(self, player):
        """Update all objects in the room."""
        # Update AI for all enemies in this room
        for enemy in self.enemies:
            enemy.update_ai(player, self.width, self.height)

    def draw(self, screen):
        """Draw everything in the room."""
        # Draw all sprites at once
        self.all_sprites.draw(screen)

    def add_player(self, player):
        """Adds the player sprite to this room's sprite group."""
        self.all_sprites.add(player)

    def remove_player(self, player):
        """Removes the player sprite from this room's sprite group."""
        self.all_sprites.remove(player)
