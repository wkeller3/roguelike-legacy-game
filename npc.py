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
        # --- Load the entire node structure ---
        self.dialogue_nodes = template_data.get("dialogue_nodes", {})

        # Visual representation
        self.image = pygame.Surface((32, 32))
        self.image.fill(C.YELLOW)
        self.rect = self.image.get_rect(center=pos)
