# gamemap.py
import random
from room import Room


class GameMap:
    """
    Manages the collection of all rooms, now using procedural generation
    to create a unique dungeon layout.
    """

    def __init__(self, max_rooms, screen_width, screen_height):
        """
        Args:
            max_rooms (int): The number of rooms to generate for the dungeon.
            screen_width (int): Pixel width of the screen.
            screen_height (int): Pixel height of the screen.
        """
        self.max_rooms = max_rooms
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.rooms = {}
        # The player always starts in the room at coordinates (0, 0)
        self.current_room_coords = (0, 0)

        # --- A set to store the coordinates of visited rooms ---
        self.explored_rooms = set()

        self._generate_dungeon()

        # After generating, mark the starting room as explored
        self.explored_rooms.add((0, 0))

        self._generate_dungeon()

    def _generate_dungeon(self):
        """
        Creates a dungeon using the "Drunkard's Walk" algorithm.
        The layout will be different every time.
        """
        print("--- Generating new dungeon ---")

        # Start at (0,0) and create the first room
        digger_x, digger_y = 0, 0
        self.rooms[(digger_x, digger_y)] = Room(self.screen_width, self.screen_height)
        num_rooms_created = 1

        while num_rooms_created < self.max_rooms:
            # Choose a random direction to step: N, S, E, W
            (dx, dy) = random.choice([(0, -1), (0, 1), (1, 0), (-1, 0)])

            # Move the digger to a new potential room location
            new_x = digger_x + dx
            new_y = digger_y + dy

            # If this spot hasn't been carved out yet, create a new room
            if (new_x, new_y) not in self.rooms:
                new_room = Room(self.screen_width, self.screen_height)
                self.rooms[(new_x, new_y)] = new_room
                num_rooms_created += 1
                print(
                    f"Created room #{num_rooms_created} at ({new_x}, {new_y}) with {len(new_room.enemies)} enemies."
                )

            # IMPORTANT: The digger always moves to the new spot, even if a
            # room was already there. This allows corridors to connect.
            digger_x, digger_y = new_x, new_y

        print("--- Dungeon generation complete! ---")

    def get_current_room(self):
        """Returns the Room object for the player's current coordinates."""
        return self.rooms.get(self.current_room_coords)  # .get() is safer

    def move_to_room(self, dx, dy):
        """
        Updates the current room coordinates and returns the new room.
        Returns None if the move is out of bounds.
        """
        new_x = self.current_room_coords[0] + dx
        new_y = self.current_room_coords[1] + dy

        if (new_x, new_y) in self.rooms:
            self.current_room_coords = (new_x, new_y)
            return self.get_current_room()

        return None
