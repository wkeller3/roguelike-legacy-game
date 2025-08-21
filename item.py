# item.py
from object import Object


class Item(Object):
    """A base class for all items."""

    def __init__(self, item_id, name, value, item_type):
        super().__init__(
            object_id=item_id,
            name=name,
            value=value,
            object_type=item_type,  # Specify the type as 'item'
        )
