# entity.py
import pygame
import constants as C
import copy
from gene import StatGene, TraitGene


class BaseEntity(pygame.sprite.Sprite):
    """
    A base class for all entities in the game (player, enemies, NPCs).
    Contains shared attributes like health, genome, and helper methods.
    """

    def __init__(self, name, pos_x, pos_y):
        super().__init__()
        self.name = name
        self.image = pygame.Surface(C.SPRITE_SIZE)
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

        self.health = 1
        self.max_health = 1
        self.genome = {}
        self.equipped_weapon = None
        self.is_defending = False

    def get_stat(self, stat_id):
        """Safely gets a stat value from the genome."""
        gene = self.genome.get(stat_id)
        return gene.value if isinstance(gene, StatGene) else 0

    def has_trait(self, trait_id):
        """Checks if a specific trait exists in the genome."""
        return trait_id in self.genome

    def get_stat_genes(self):
        """Returns a sorted list of all StatGene objects in the genome."""
        genes = [g for g in self.genome.values() if isinstance(g, StatGene)]
        return sorted(genes, key=lambda g: g.name)

    def get_trait_genes(self):
        """Returns a sorted list of all TraitGene objects in the genome."""
        genes = [g for g in self.genome.values() if isinstance(g, TraitGene)]
        return sorted(genes, key=lambda g: g.name)

    def move(self, dx, dy, screen_width, screen_height):
        """Moves the entity and keeps it on screen."""
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
