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
        sprite_filename = template_data.get("sprite")
        # --- Load the entire node structure ---
        self.dialogue_nodes = template_data.get("dialogue_nodes", {})

        self.npc_type = template_data.get("npc_type", "dialogue")
        self.vendor_id = template_data.get("vendor_id", None)

        # Visual representation
        # --- Load image from file if it exists ---
        if sprite_filename:
            # .convert_alpha() is important for handling transparency
            loaded_image = pygame.image.load(sprite_filename).convert_alpha()
            self.image = pygame.transform.scale(loaded_image, C.SPRITE_SIZE)
        else:
            # Fallback to the colored square if no sprite is defined
            self.image = pygame.Surface((32, 32))
            self.image.fill(C.YELLOW)
        self.rect = self.image.get_rect(center=pos)

        self.inventory = []
