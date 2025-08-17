# npc.py
import pygame
import constants as C


class NPC(pygame.sprite.Sprite):
    """
    A generic NPC class that is configured using a data template.
    """

    def __init__(self, template_data):
        super().__init__()

        # Configure from the data dictionary
        self.name = template_data["name"]
        pos = tuple(template_data["pos"])
        self.dialogue = template_data.get("dialogue", ["..."])

        # Visual representation
        self.image = pygame.Surface((32, 32))
        self.image.fill(C.YELLOW)
        self.rect = self.image.get_rect(center=pos)
