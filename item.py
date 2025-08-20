# item.py


class Item:
    """A base class for all items."""

    def __init__(self, item_id, name, value):
        self.item_id = item_id
        self.name = name
        self.value = value  # The base value in gold
