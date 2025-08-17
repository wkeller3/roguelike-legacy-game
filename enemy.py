# enemy.py
import pygame
import random
import math
from weapon import Weapon
import constants as C


class Enemy(pygame.sprite.Sprite):
    """
    This is the BASE class for all enemies. It contains all the shared logic
    for AI, movement, and basic attributes.
    """

    def __init__(self, pos_x, pos_y):
        super().__init__()
        # These are placeholders; they will be defined by the subclasses.
        self.health = 1
        self.stats = {}
        self.equipped_weapon = None
        self.speed = 1
        self.sight_radius = 100
        self.chase_radius = 150

        # Default appearance (can be overridden by subclasses)
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 255, 255))  # Default to white
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)

        # Shared AI and Combat State
        self.state = "WANDERING"
        self.is_charging_attack = False
        self.wander_direction = self.get_random_direction()
        self.wander_timer = 0
        self.wander_duration = random.randint(60, 180)

    def get_random_direction(self):
        # ... (This method is unchanged) ...
        angle = random.uniform(0, 2 * math.pi)
        return (math.cos(angle), math.sin(angle))

    def update_ai(self, player, screen_width, screen_height):
        # ... (This entire method is unchanged, as it's shared by all enemies) ...
        dist_to_player = math.hypot(
            self.rect.centerx - player.rect.centerx,
            self.rect.centery - player.rect.centery,
        )
        if self.state == "WANDERING":
            if dist_to_player < self.sight_radius:
                self.state = "CHASING"
                return
            self.wander_timer += 1
            if self.wander_timer >= self.wander_duration:
                self.wander_direction = self.get_random_direction()
                self.wander_timer = 0
                self.wander_duration = random.randint(60, 180)
            dx = self.wander_direction[0] * self.speed
            dy = self.wander_direction[1] * self.speed
            self.move(dx, dy, screen_width, screen_height)
        elif self.state == "CHASING":
            if dist_to_player > self.chase_radius:
                self.state = "WANDERING"
                return
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            norm = math.hypot(dx, dy)
            if norm > 0:
                dx /= norm
                dy /= norm
            self.move(dx * self.speed, dy * self.speed, screen_width, screen_height)

    def move(self, dx, dy, screen_width, screen_height):
        # ... (This method is unchanged) ...
        self.rect.x += dx
        self.rect.y += dy
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height


# --- Specific Enemy Type Subclasses ---


class Goblin(Enemy):
    """A Goblin is a fast, common enemy with stat variations."""

    def __init__(self, pos_x, pos_y):
        # First, run the __init__ of the parent Enemy class
        super().__init__(pos_x, pos_y)

        # Now, customize the stats for a Goblin
        self.image.fill(C.RED)  # Goblins are red

        # Add random variation to stats
        self.health = random.randint(30, 45)
        self.stats = {
            "Strength": random.randint(2, 4),
            "Dexterity": random.randint(3, 6),
        }
        self.speed = random.uniform(2.0, 2.5)  # Slight speed variance
        self.sight_radius = 300
        self.chase_radius = 350
        self.equipped_weapon = Weapon(
            name="Rusty Dagger",
            base_damage=(3, 6),
            crit_chance=0.1,
            crit_multiplier=1.5,
        )


class Orc(Enemy):
    """An Orc is a slower, tougher enemy."""

    def __init__(self, pos_x, pos_y):
        # Run the parent __init__ method
        super().__init__(pos_x, pos_y)

        # Customize for an Orc
        self.image.fill(C.GREEN)  # Orcs are green

        self.health = random.randint(60, 80)  # Much tougher
        self.stats = {
            "Strength": random.randint(5, 8),  # Much stronger
            "Dexterity": random.randint(1, 3),  # Much clumsier
        }
        self.speed = random.uniform(1.2, 1.6)  # Slower
        self.sight_radius = 200  # Worse eyesight
        self.chase_radius = 250
        self.equipped_weapon = Weapon(
            name="Crude Axe", base_damage=(5, 10), crit_chance=0.05, crit_multiplier=1.5
        )
