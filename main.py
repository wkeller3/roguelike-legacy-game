# main.py

import pygame
import json
import constants as C
from weapon import Weapon
from ui_elements import Button
from states import (
    CharCreationState,
    ExploringState,
    CombatState,
    GameOverState,
    OverworldState,
    TownState,
)
from hero import Hero
from gamemap import GameMap

# --- Developer flag to bypass character creation for quick testing ---
DEV_SKIP_CHAR_CREATION = True


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

        self.states = {}
        self.current_state = None
        self.persistent_data = {}

    def setup_states(self):
        """Initializes all the game states and sets the starting state."""
        # --- FIX: Define ALL possible states first ---
        self.states = {
            "TOWN": TownState,
            "CHAR_CREATION": CharCreationState,
            "EXPLORING": ExploringState,
            "COMBAT": CombatState,
            "GAME_OVER": GameOverState,
            "OVERWORLD": OverworldState,
        }

        # --- THEN, decide which state to start in ---
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
            game_map = GameMap(
                max_rooms=15, screen_width=C.SCREEN_WIDTH, screen_height=C.SCREEN_HEIGHT
            )

            self.persistent_data = {"player": player, "game_map": game_map}
            self.current_state = self.states["TOWN"](self.persistent_data)
        else:
            char_creation_data = self.load_char_creation_data()
            self.current_state = self.states["CHAR_CREATION"](char_creation_data)

    def load_char_creation_data(self):
        """Loads and prepares all data needed for the character creation screen."""
        with open("weapons.json", "r") as f:
            weapons_data = json.load(f)
        weapon_objects = [
            Weapon(
                name=d["name"],
                base_damage=tuple(d["base_damage"]),
                crit_chance=d["crit_chance"],
                crit_multiplier=d["crit_multiplier"],
            )
            for d in weapons_data
        ]
        data = {
            "name": "",
            "name_active": False,
            "points_to_spend": 10,
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

    def flip_state(self):
        """Handles the transition from one state to the next."""
        next_state_name = self.current_state.next_state
        self.current_state.done = False

        if next_state_name == "CHAR_CREATION":
            # If restarting, we need to reload the initial data
            char_creation_data = self.load_char_creation_data()
            self.current_state = self.states[next_state_name](char_creation_data)
        else:
            # For all other transitions, pass the persistent data along
            self.persistent_data = self.current_state.persistent_data
            self.current_state = self.states[next_state_name](self.persistent_data)

    def run(self):
        """The main game loop."""
        dt = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.current_state.handle_events(event)

            self.current_state.update(dt)

            if self.current_state.done:
                self.flip_state()
            if self.current_state.quit:
                self.running = False

            self.current_state.draw(self.screen)
            pygame.display.flip()
            dt = self.clock.tick(60) / 1000


if __name__ == "__main__":
    game = Game()
    game.setup_states()
    game.run()
    pygame.quit()
