# gamemap.py
import random
from room import Room


class GameMap:
    """
    Manages the collection of all rooms, now using procedural generation
    to create a unique dungeon layout.
    """

    def __init__(
        self, min_rooms, max_rooms, screen_width, screen_height, entry_direction
    ):
        """
        Args:
            max_rooms (int): The number of rooms to generate for the dungeon.
            screen_width (int): Pixel width of the screen.
            screen_height (int): Pixel height of the screen.
            entry_direction (str): The side from which the player enters ('NORTH', 'SOUTH', etc.)
        """
        self.num_rooms = random.randint(min_rooms, max_rooms)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.entry_direction = entry_direction  # Store the entry direction

        self.rooms = {}
        self.current_room_coords = (0, 0)
        self.explored_rooms = set()

        self._generate_dungeon()

    def _generate_dungeon(self):
        """
        Creates a dungeon, keeping the exit clear based on the entry direction
        and guaranteeing a path away from the entrance.
        """
        print("--- Generating new dungeon ---")

        # Determine the single forbidden tile for the exit
        exit_map = {"NORTH": (0, -1), "SOUTH": (0, 1), "WEST": (-1, 0), "EAST": (1, 0)}
        opposite_map = {
            "NORTH": (0, 1),
            "SOUTH": (0, -1),
            "WEST": (1, 0),
            "EAST": (-1, 0),
        }

        forbidden_tile = exit_map[self.entry_direction]

        # Create the starting room
        digger_x, digger_y = 0, 0
        self.rooms[(digger_x, digger_y)] = Room(self.screen_width, self.screen_height)
        self.explored_rooms.add((digger_x, digger_y))
        num_rooms_created = 1

        # --- uarantee a path away from the entrance ---
        # Force the first step to be away from the entry direction
        first_step = opposite_map[self.entry_direction]
        digger_x += first_step[0]
        digger_y += first_step[1]
        self.rooms[(digger_x, digger_y)] = Room(self.screen_width, self.screen_height)
        num_rooms_created += 1
        print(f"Created entrance corridor at ({digger_x}, {digger_y})")

        while num_rooms_created < self.num_rooms:
            directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
            (dx, dy) = random.choice(directions)

            new_x = digger_x + dx
            new_y = digger_y + dy

            # Check if the new spot is the single forbidden exit tile
            if (new_x, new_y) == forbidden_tile:
                continue

            if (new_x, new_y) not in self.rooms:
                self.rooms[(new_x, new_y)] = Room(self.screen_width, self.screen_height)
                num_rooms_created += 1

            digger_x, digger_y = new_x, new_y

        print(
            f"--- Dungeon generation complete! Created a dungeon with {self.num_rooms} rooms ---"
        )

    def get_current_room(self):
        """Returns the Room object for the player's current coordinates."""
        return self.rooms.get(self.current_room_coords)

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
