class Object:
    """A base class for all objects."""

    def __init__(self, object_id, name, value, object_type):
        self.object_id = object_id
        self.name = name
        self.value = value  # The base value in gold
        self.object_type = object_type  # e.g., 'weapon', 'armor', 'consumable', 'junk'
