# hero.py

import copy
import pygame
import constants as C
from entity import BaseEntity
from factories import ITEM_TEMPLATES, GENE_TEMPLATES
from gene import StatGene, TraitGene
import copy


# Make the Hero class a Pygame Sprite for 2D game object functionality.
class Hero(BaseEntity):
    """
    Represents the hero, now as a movable sprite.
    Inherits from BaseEntity.
    """

    def __init__(self, first_name, family_name, pos_x, pos_y):
        # Use the full name for the base entity
        super().__init__(name=f"{first_name} {family_name}", pos_x=pos_x, pos_y=pos_y)

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
        # possible_traits = ["Brave", "Cautious", "Avaricious", "Kind", "Clever"]
        self.experience = 0

    # def get_stat(self, stat_id):
    #     """Safely gets a stat value from the genome."""
    #     gene = self.genome.get(stat_id)
    #     return gene.value if isinstance(gene, StatGene) else 0

    # def has_trait(self, trait_id):
    #     """Checks if a specific trait exists in the genome."""
    #     return trait_id in self.genome

    # def get_stat_genes(self):
    #     """Returns a sorted list of all StatGene objects in the genome."""
    #     genes = [g for g in self.genome.values() if isinstance(g, StatGene)]
    #     return sorted(genes, key=lambda g: g.name)

    # def get_trait_genes(self):
    #     """Returns a sorted list of all TraitGene objects in the genome."""
    #     genes = [g for g in self.genome.values() if isinstance(g, TraitGene)]
    #     return sorted(genes, key=lambda g: g.name)

    # def move(self, dx, dy, screen_width, screen_height):
    #     """
    #     Moves the hero by a given amount (dx, dy) and keeps them on screen.
    #     """
    #     self.rect.x += dx
    #     self.rect.y += dy

    #     # Boundary checking to prevent the hero from leaving the screen
    #     if self.rect.left < 0:
    #         self.rect.left = 0
    #     if self.rect.right > screen_width:
    #         self.rect.right = screen_width
    #     if self.rect.top < 0:
    #         self.rect.top = 0
    #     if self.rect.bottom > screen_height:
    #         self.rect.bottom = screen_height

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
            "genome": {
                gene_id: gene.value if isinstance(gene, StatGene) else True
                for gene_id, gene in self.genome.items()
            },
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
        player.genome = {}
        if "genome" in data:
            for gene_id, value in data["genome"].items():
                template_gene = GENE_TEMPLATES[gene_id]
                new_gene = copy.deepcopy(
                    template_gene
                )  # Use deepcopy to avoid modifying the template
                if isinstance(new_gene, StatGene):
                    new_gene.value = value
                player.genome[gene_id] = new_gene
        if data["equipped_weapon_id"]:
            player.equipped_weapon = ITEM_TEMPLATES[data["equipped_weapon_id"]]
        return player
