# gene.py


class Gene:
    """A base class for all inheritable attributes."""

    def __init__(self, gene_id, name, gene_type):
        self.gene_id = gene_id
        self.name = name
        self.gene_type = gene_type


class StatGene(Gene):
    """A gene that represents a numerical stat."""

    def __init__(self, gene_id, name, gene_type, value, min_value, max_value):
        super().__init__(gene_id, name, gene_type)
        self.value = value
        self.min_value = min_value
        self.max_value = max_value


class TraitGene(Gene):
    """A gene that represents a descriptive trait with passive effects."""

    def __init__(self, gene_id, name, gene_type, description, effects):
        super().__init__(gene_id, name, gene_type)
        self.description = description
        self.effects = effects  # This will be a dictionary, e.g., {"damage_bonus": 0.1}


class CosmeticGene(Gene):
    """A gene for visual features like hair or eye color."""

    def __init__(self, gene_id, name, gene_type, value):
        super().__init__(gene_id, name, gene_type)
        self.value = value
