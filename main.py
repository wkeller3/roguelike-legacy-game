# main.py

import pygame
import json
import constants as C
from gamemap import GameMap
from weapon import Weapon
from ui_elements import Button
from states import STATE_MAP, create_state
from hero import Hero
from game_context import GameContext

# --- Developer flag to bypass character creation for quick testing ---
DEV_SKIP_CHAR_CREATION = False


class Game:
    """
    The main game class that manages the game window, the main loop,
    and the state machine.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        pygame.display.set_caption("Legacy of the Cursed")
        self.clock = pygame.time.Clock()
        self.running = True

        self.state_stack = []
        self.current_state = None
        self.context = GameContext()

    def setup_states(self):
        """Initializes all the game states and sets the starting state."""
        if DEV_SKIP_CHAR_CREATION:
            player = Hero(
                first_name="Dev",
                family_name="Tester",
                pos_x=100,
                pos_y=C.SCREEN_HEIGHT / 2,
            )
            player.stats = {"Strength": 5, "Dexterity": 5, "Intelligence": 5, "Luck": 5}
            player.equipped_weapon = Weapon(
                name="Developer Sword",
                base_damage=(10, 15),
                crit_chance=0.1,
                crit_multiplier=2.0,
            )

            self.context.player = player
            self.state_stack.append(create_state("TOWN", self))
        else:
            char_creation_data = self.load_char_creation_data()
            self.state_stack.append(create_state("MAIN_MENU", self))

    def load_char_creation_data(self):
        """Loads and prepares all data needed for the character creation screen."""
        with open("weapons.json", "r") as f:
            weapons_data = json.load(f)
        starter_weapon_ids = ["broadsword", "twin_daggers", "iron_staff"]
        weapon_objects = [
            Weapon(
                name=weapons_data[w_id]["name"],
                base_damage=tuple(weapons_data[w_id]["base_damage"]),
                crit_chance=weapons_data[w_id]["crit_chance"],
                crit_multiplier=weapons_data[w_id]["crit_multiplier"],
            )
            for w_id in starter_weapon_ids
        ]
        data = {
            "name": "",
            "name_active": False,
            "points_to_spend": C.CHAR_CREATION_STARTING_POINTS,
            "stats": {"Strength": 1, "Dexterity": 1, "Intelligence": 1, "Luck": 1},
            "weapon_choices": weapon_objects,
            "selected_weapon_idx": 0,
            "ui_elements": {},
        }

        font_text = pygame.font.Font(None, C.FONT_SIZE_TEXT)
        font_title = pygame.font.Font(None, C.FONT_SIZE_TITLE)
        data["ui_elements"]["name_box"] = pygame.Rect(50, 80, 300, 40)
        stat_y_start = 180
        for i, stat in enumerate(data["stats"]):
            y_pos = stat_y_start + i * 40
            data["ui_elements"][f"{stat}_plus"] = Button(
                250, y_pos, 30, 30, "+", font_text, C.GREEN, C.GRAY
            )
            data["ui_elements"][f"{stat}_minus"] = Button(
                290, y_pos, 30, 30, "-", font_text, C.RED, C.GRAY
            )
        weapon_y_start = 180
        for i in range(len(data["weapon_choices"])):
            data["ui_elements"][f"weapon_{i}_rect"] = pygame.Rect(
                450, weapon_y_start + i * 60, 320, 50
            )
        data["ui_elements"]["done_button"] = Button(
            C.SCREEN_WIDTH / 2 - 100,
            C.SCREEN_HEIGHT - 80,
            200,
            50,
            "Create Hero",
            font_title,
            C.GREEN,
            C.GRAY,
        )
        return data

    def get_active_state(self):
        return self.state_stack[-1]

    def push_state(self, state_name, **kwargs):
        """Pushes a new state onto the stack."""
        new_state = create_state(state_name, self, **kwargs)
        self.state_stack.append(new_state)

    def pop_state(self):
        """Pops the top state off the stack."""
        if len(self.state_stack) > 1:
            self.state_stack.pop()

    def flip_state(self):
        """Transitions to a completely new state, clearing the stack, using the factory."""
        next_state_name = self.get_active_state().next_state

        self.state_stack = []  # Clear the stack

        if next_state_name == "CHAR_CREATION":
            char_data = self.load_char_creation_data()
            self.state_stack.append(
                create_state("CHAR_CREATION", self, initial_data=char_data)
            )
        else:
            self.state_stack.append(create_state(next_state_name, self))

    def load_game_data(self):
        """Reads the save file and reconstructs the game state using object methods."""
        try:
            with open("savegame.json", "r") as f:
                save_data = json.load(f)

            # Reconstruct Player and GameMap
            player = Hero.from_dict(save_data["player_data"])
            game_map = None
            if save_data["map_data"]:
                game_map = GameMap(
                    screen_width=C.SCREEN_WIDTH,
                    screen_height=C.SCREEN_HEIGHT,
                    map_data=save_data["map_data"],
                )

            # Restore player's current room in the map if it exists
            if game_map:
                saved_room_coords = save_data["player_data"]["position"]["room_coords"]
                if saved_room_coords:
                    game_map.current_room_coords = tuple(saved_room_coords)

            # Populate the context object
            self.context.player = player
            self.context.game_map = game_map
            starting_state = save_data["last_state"]

            return starting_state
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Could not load save game: {e}")
            return None, None

    def load_and_start_from_save(self):
        """Loads data and flips to the appropriate game state."""
        starting_state_name = self.load_game_data()
        if starting_state_name:
            self.state_stack = []
            new_state = create_state(starting_state_name, self)
            self.state_stack.append(new_state)

    def save_game_data(self):
        """Gathers all necessary data using object methods and saves it to a file."""
        active_state = self.get_active_state()
        gameplay_state = active_state
        if hasattr(active_state, "previous_state"):
            gameplay_state = active_state.previous_state

        player = self.context.player
        game_map = self.context.game_map

        if not player:
            print("Cannot save: No active player found.")
            return

        # Get the current state key for saving
        state_key_to_save = next(
            (
                key
                for key, value in STATE_MAP.items()
                if isinstance(gameplay_state, value)
            ),
            None,
        )
        # Get the current room coordinates, which might be None if not in a dungeon
        current_room_coords = game_map.current_room_coords if game_map else None
        save_data = {
            "player_data": player.to_dict(current_room_coords=current_room_coords),
            "map_data": game_map.to_dict() if game_map else None,
            "last_state": state_key_to_save,
        }

        with open("savegame.json", "w") as f:
            json.dump(save_data, f, indent=4)
        print("Game saved successfully!")

    def run(self):
        """The main game loop."""
        dt = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.get_active_state().handle_events(event)

            self.get_active_state().update(dt)

            if self.get_active_state().quit:
                self.running = False
            elif self.get_active_state().done:
                self.flip_state()

            self.get_active_state().draw(self.screen)

            pygame.display.flip()
            dt = self.clock.tick(C.FPS) / 1000


if __name__ == "__main__":
    game = Game()
    game.setup_states()
    game.run()
    pygame.quit()
