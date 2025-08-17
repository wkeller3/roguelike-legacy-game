# enemy.py
import pygame
import random
import math
from weapon import Weapon
import constants as C


class Enemy(pygame.sprite.Sprite):
    """
    A generic Enemy class that is configured using a data template.
    All enemies share this same class and logic.
    """

    def __init__(self, pos_x, pos_y, template_data):
        super().__init__()

        # --- Configure from Template ---
        self.name = template_data["name"]

        # Appearance
        self.image = pygame.Surface((32, 32))
        self.image.fill(tuple(template_data["color"]))
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

        # Stats with random variation
        self.health = random.randint(*template_data["health_range"])
        self.stats = {
            "Strength": random.randint(*template_data["stats"]["Strength"]),
            "Dexterity": random.randint(*template_data["stats"]["Dexterity"]),
        }
        self.speed = random.uniform(*template_data["speed_range"])
        self.sight_radius = template_data["sight_radius"]
        self.chase_radius = self.sight_radius + 50
        self.gold_drop_range = template_data.get("gold_drop_range", [1, 1])

        # Equipment
        w_data = template_data["weapon"]
        self.equipped_weapon = Weapon(
            name=w_data["name"],
            base_damage=tuple(w_data["base_damage"]),
            crit_chance=w_data["crit_chance"],
            crit_multiplier=w_data["crit_multiplier"],
        )

        # Shared AI and Combat State
        self.state = "WANDERING"
        self.is_charging_attack = False
        self.wander_direction = self.get_random_direction()
        self.wander_timer = 0
        self.wander_duration = random.randint(60, 180)

    def get_random_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        return (math.cos(angle), math.sin(angle))

    def update_ai(self, player, screen_width, screen_height):
        # ... (This entire method is unchanged) ...
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
