# states.py

import pygame
import random
import constants as C
from factories import ITEM_TEMPLATES, VENDOR_INVENTORIES
from hero import Hero
from item import Consumable, Weapon
from npc import NPC
from gamemap import GameMap
from combat import resolve_attack
from map_view import draw_map
from room import Room
import json
from ui_elements import (
    Button,
    MainMenu,
    PauseMenu,
    ShopUI,
    TextBox,
    DialogueBox,
    CharacterSheet,
    SettingsMenu,
)


class BaseState:
    """
    The base class for all states, now using the GameContext.
    """

    def __init__(self, game):
        self.game = game
        self.context = game.context
        self.done = False
        self.quit = False
        self.next_state = None

    def handle_events(self, event):
        """Handle a single user event. Called for each event in the event queue."""
        if event.type == pygame.QUIT:
            self.quit = True

    def update(self, dt):
        pass

    def draw(self, screen):
        pass


class CharCreationState(BaseState):
    """The character creation state."""

    def __init__(self, game, initial_data):
        super().__init__(game)
        self.data = initial_data
        self.font_title = pygame.font.Font(None, C.FONT_SIZE_TITLE)
        self.font_header = pygame.font.Font(None, C.FONT_SIZE_HEADER)
        self.font_text = pygame.font.Font(None, C.FONT_SIZE_TEXT)

    def handle_events(self, event):
        super().handle_events(event)
        # Handle button clicks using the Button class's method
        for stat in self.data["stats"]:
            if self.data["ui_elements"][f"{stat}_plus"].handle_event(event):
                if self.data["points_to_spend"] > 0:
                    self.data["stats"][stat] += 1
                    self.data["points_to_spend"] -= 1
            if self.data["ui_elements"][f"{stat}_minus"].handle_event(event):
                if self.data["stats"][stat] > 1:
                    self.data["stats"][stat] -= 1
                    self.data["points_to_spend"] += 1
        if self.data["ui_elements"]["done_button"].handle_event(event):
            # Create the hero and prepare the persistent data for the next state
            player = Hero(
                first_name=self.data["name"],
                family_name="The Bold",
                pos_x=100,
                pos_y=C.INTERNAL_HEIGHT / 2,
            )
            player.stats = self.data["stats"]
            player.equipped_weapon = self.data["weapon_choices"][
                self.data["selected_weapon_idx"]
            ]

            # Populate the shared game context
            self.context.player = player

            self.done = True
            self.next_state = "TOWN"
        # Handle other mouse clicks (name box, weapon selection)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.data["ui_elements"]["name_box"].collidepoint(event.pos):
                self.data["name_active"] = True
            else:
                self.data["name_active"] = False
            for i in range(len(self.data["weapon_choices"])):
                if self.data["ui_elements"][f"weapon_{i}_rect"].collidepoint(event.pos):
                    self.data["selected_weapon_idx"] = i
        # Handle keyboard input for the name box
        if event.type == pygame.KEYDOWN and self.data["name_active"]:
            if event.key == pygame.K_BACKSPACE:
                self.data["name"] = self.data["name"][:-1]
            elif len(self.data["name"]) < C.CHAR_CREATION_MAX_NAME_LENGTH:
                self.data["name"] += event.unicode

    def update(self, dt):
        # Update the 'done' button's disabled state based on completion criteria
        is_creation_complete = (
            self.data["points_to_spend"] == 0 and self.data["name"].strip() != ""
        )
        self.data["ui_elements"]["done_button"].is_disabled = not is_creation_complete

    def draw(self, screen):
        screen.fill(C.ROOM_COLOR)
        # Titles
        title_text = self.font_title.render("Create Your Legacy", True, C.WHITE)
        screen.blit(title_text, (C.INTERNAL_WIDTH / 2 - title_text.get_width() / 2, 20))
        # Name Section
        pygame.draw.rect(
            screen,
            C.GRAY,
            self.data["ui_elements"]["name_box"],
            2 if not self.data["name_active"] else 3,
        )
        name_text = self.font_text.render(self.data["name"], True, C.WHITE)
        screen.blit(
            name_text,
            (
                self.data["ui_elements"]["name_box"].x + 10,
                self.data["ui_elements"]["name_box"].y + 8,
            ),
        )
        # Stats Section
        points_text = self.font_header.render(
            f"Attribute Points: {self.data['points_to_spend']}", True, C.WHITE
        )
        screen.blit(points_text, (50, 140))
        for i, (stat, value) in enumerate(self.data["stats"].items()):
            y_pos = 180 + i * 40
            stat_text = self.font_text.render(f"{stat}: {value}", True, C.WHITE)
            screen.blit(stat_text, (50, y_pos + 5))
            self.data["ui_elements"][f"{stat}_plus"].draw(screen)
            self.data["ui_elements"][f"{stat}_minus"].draw(screen)
        # Weapon Section
        weapon_text = self.font_header.render("Choose a Weapon:", True, C.WHITE)
        screen.blit(weapon_text, (450, 140))
        for i, weapon in enumerate(self.data["weapon_choices"]):
            rect = self.data["ui_elements"][f"weapon_{i}_rect"]
            is_selected = i == self.data["selected_weapon_idx"]
            pygame.draw.rect(
                screen,
                C.WHITE if is_selected else C.GRAY,
                rect,
                3 if is_selected else 2,
            )
            weapon_name_text = self.font_text.render(weapon.name, True, C.WHITE)
            screen.blit(weapon_name_text, (rect.x + 10, rect.y + 12))
        # Done Button
        self.data["ui_elements"]["done_button"].draw(screen)


class MainMenuState(BaseState):
    """The state for the main menu of the game."""

    def __init__(self, game):
        super().__init__(game)
        self.menu_ui = MainMenu(game)

    def handle_events(self, event):
        super().handle_events(event)
        self.menu_ui.handle_event(event)

    def draw(self, screen):
        screen.fill(C.ROOM_COLOR)
        self.menu_ui.draw(screen)


class GameplayState(BaseState):
    """Intermediate class for states that share the main gameplay data."""

    def __init__(self, game):
        super().__init__(game)
        self.player = self.context.player
        self.game_map = self.context.game_map
        self.font_text = pygame.font.Font(None, C.FONT_SIZE_TEXT)

    def draw_hud(self, screen):
        """Draws the common Heads-Up Display."""
        y_offset = 20
        # Health
        health_color = C.GREEN if not self.player.is_defending else (100, 200, 255)
        screen.blit(
            self.font_text.render(
                f"Health: {self.player.health}/{self.player.max_health}",
                True,
                health_color,
            ),
            (20, y_offset),
        )
        # Gold
        y_offset += 30
        gold_text = self.font_text.render(f"Gold: {self.player.gold}", True, C.GOLD)
        screen.blit(gold_text, (20, y_offset))


class TownState(GameplayState):
    """The state for the main town or hub area."""

    def __init__(self, game):
        super().__init__(game)
        self.town_room = Room(C.INTERNAL_WIDTH, C.INTERNAL_HEIGHT, room_type="town")
        self.town_room.add_player(self.player)

        # --- Load NPCs from the data file ---
        self._load_npcs()
        # Player repositioning logic
        entry_point = getattr(self.context, "entry_direction", "CENTER")
        if entry_point == "NORTH":
            self.player.rect.midtop = (C.INTERNAL_WIDTH / 2, 20)
        elif entry_point == "SOUTH":
            self.player.rect.midbottom = (C.INTERNAL_WIDTH / 2, C.INTERNAL_HEIGHT - 20)
        elif entry_point == "WEST":
            self.player.rect.midleft = (20, C.INTERNAL_HEIGHT / 2)
        elif entry_point == "EAST":
            self.player.rect.midright = (C.INTERNAL_WIDTH - 20, C.INTERNAL_HEIGHT / 2)
        else:  # Default for new game start
            self.player.rect.center = (C.INTERNAL_WIDTH / 2, C.INTERNAL_HEIGHT / 2)

        hint_rect = pygame.Rect(0, C.INTERNAL_HEIGHT - 60, C.INTERNAL_WIDTH, 50)
        self.interaction_hint = TextBox("", hint_rect, self.font_text)
        self.interaction_hint.is_visible = False
        self.dialogue_box = DialogueBox()
        self.ui_elements = [self.interaction_hint, self.dialogue_box]
        self.nearby_npc = None

    def _load_npcs(self):
        """Loads NPC data from the JSON file and populates the town."""
        with open("npcs.json", "r") as f:
            all_npc_data = json.load(f)

        # Get the list of NPCs specifically for the "Town" location
        town_npcs = all_npc_data.get("Town", [])
        for npc_data in town_npcs:
            self.town_room.add_npc(NPC(template_data=npc_data))

    def handle_events(self, event):
        super().handle_events(event)
        if self.dialogue_box.is_active:
            self.dialogue_box.handle_event(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.push_state("PAUSE")
            if event.key == pygame.K_e:
                if self.nearby_npc:
                    if self.nearby_npc.npc_type == "vendor":
                        self.game.push_state("SHOP", vendor=self.nearby_npc)
                    else:  # Default to dialogue
                        self.dialogue_box.start_dialogue(self.nearby_npc)
            if event.key == pygame.K_c:
                self.game.push_state("CHAR_SHEET")

    def update(self, dt):
        # --- Pause player movement and exits during dialogue ---
        if self.dialogue_box.is_active:
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -C.PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = C.PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -C.PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = C.PLAYER_SPEED
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, C.INTERNAL_WIDTH, C.INTERNAL_HEIGHT)

        # --- Check for nearby NPCs instead of just collision ---
        self.nearby_npc = None  # Reset each frame
        for npc in self.town_room.npcs:
            # Check distance between player and NPC centers
            distance = pygame.math.Vector2(self.player.rect.center).distance_to(
                npc.rect.center
            )
            if distance < C.NPC_INTERACTION_RADIUS:
                self.nearby_npc = npc
                break  # Found the closest one, no need to check others

        if self.nearby_npc:
            self.interaction_hint.set_text(f"[E] Talk to {self.nearby_npc.name}")
            self.interaction_hint.is_visible = True
        else:
            self.interaction_hint.is_visible = False

        exit_direction = None
        if self.player.rect.top <= 0:
            exit_direction = "NORTH"
        elif self.player.rect.bottom >= C.INTERNAL_HEIGHT:
            exit_direction = "SOUTH"
        elif self.player.rect.left <= 0:
            exit_direction = "WEST"
        elif self.player.rect.right >= C.INTERNAL_WIDTH:
            exit_direction = "EAST"

        if exit_direction:
            self.context.exit_to_overworld_from = "Town"
            self.context.overworld_entry_direction = exit_direction
            self.done = True
            self.next_state = "OVERWORLD"

    def draw(self, screen):
        screen.fill(C.ROOM_COLOR)
        self.town_room.draw(screen)
        self.draw_hud(screen)
        # Draw the UI elements
        for element in self.ui_elements:
            element.draw(screen)


class OverworldState(GameplayState):
    def __init__(self, game):
        super().__init__(game)
        self.pois = {
            "Town": {"rect": pygame.Rect(180, 280, 100, 80), "target_state": "TOWN"},
            "Dungeon": {
                "rect": pygame.Rect(520, 280, 100, 80),
                "target_state": "EXPLORING",
            },
        }
        self.player_avatar = pygame.Rect(0, 0, 20, 20)
        # --- Position avatar dynamically based on exit information ---
        exit_location = getattr(self.context, "exit_to_overworld_from", "Town")
        entry_direction = getattr(self.context, "overworld_entry_direction", "SOUTH")
        poi_rect = self.pois[exit_location]["rect"]
        padding = 5
        if entry_direction == "NORTH":
            self.player_avatar.midbottom = (poi_rect.centerx, poi_rect.top - padding)
        elif entry_direction == "SOUTH":
            self.player_avatar.midtop = (poi_rect.centerx, poi_rect.bottom + padding)
        elif entry_direction == "WEST":
            self.player_avatar.midright = (poi_rect.left - padding, poi_rect.centery)
        elif entry_direction == "EAST":
            self.player_avatar.midleft = (poi_rect.right + padding, poi_rect.centery)

    def handle_events(self, event):
        super().handle_events(event)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -C.PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = C.PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -C.PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = C.PLAYER_SPEED
        if dx != 0 or dy != 0:
            self.player_avatar.move_ip(dx, dy)
        # --- Dynamic entry direction logic ---
        for name, data in self.pois.items():
            if self.player_avatar.colliderect(data["rect"]):
                # Step 1: Immediately determine the entry direction based on collision
                col_dx = self.player_avatar.centerx - data["rect"].centerx
                col_dy = self.player_avatar.centery - data["rect"].centery
                entry_direction = ""
                if abs(col_dx) > abs(col_dy):  # Horizontal collision
                    if col_dx > 0:
                        entry_direction = "EAST"
                    else:
                        entry_direction = "WEST"
                else:  # Vertical collision
                    if col_dy > 0:
                        entry_direction = "SOUTH"
                    else:
                        entry_direction = "NORTH"

                # Step 2: If entering the dungeon, generate a new map using the direction
                if name == "Dungeon":
                    new_dungeon_map = GameMap(
                        min_rooms=C.MIN_ROOMS,
                        max_rooms=C.MAX_ROOMS,
                        screen_width=C.INTERNAL_WIDTH,
                        screen_height=C.INTERNAL_HEIGHT,
                        entry_direction=entry_direction,
                    )
                    self.context.game_map = new_dungeon_map
                # Step 3: Store the entry direction for the next state to use
                self.context.entry_direction = entry_direction
                # Step 4: Trigger the state transition
                self.done = True
                self.next_state = data["target_state"]

    def draw(self, screen):
        screen.fill((20, 80, 40))
        for name, data in self.pois.items():
            pygame.draw.rect(screen, C.GRAY, data["rect"])
            name_text = self.font_text.render(name, True, C.WHITE)
            text_rect = name_text.get_rect(center=data["rect"].center)
            screen.blit(name_text, text_rect)
        pygame.draw.rect(screen, C.PLAYER_COLOR, self.player_avatar)


class ExploringState(GameplayState):
    def __init__(self, game):
        super().__init__(game)
        self.current_room = self.game_map.get_current_room()
        self.current_room.add_player(self.player)
        self.show_map = False
        # Reposition player based on how they entered the dungeon

        entry_point = getattr(self.context, "entry_direction", None)
        if entry_point:
            # If it exists, position the player accordingly
            if entry_point == "NORTH":
                self.player.rect.midtop = (C.INTERNAL_WIDTH / 2, 20)
            elif entry_point == "SOUTH":
                self.player.rect.midbottom = (
                    C.INTERNAL_WIDTH / 2,
                    C.INTERNAL_HEIGHT - 20,
                )
            elif entry_point == "WEST":
                self.player.rect.midleft = (20, C.INTERNAL_HEIGHT / 2)
            elif entry_point == "EAST":
                self.player.rect.midright = (
                    C.INTERNAL_WIDTH - 20,
                    C.INTERNAL_HEIGHT / 2,
                )
            self.context.entry_direction = None

    def handle_events(self, event):
        super().handle_events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.push_state("PAUSE")
            if event.key == pygame.K_m:
                self.show_map = not self.show_map
            elif event.key == pygame.K_c:
                self.game.push_state("CHAR_SHEET")

    def update(self, dt):
        if self.show_map:
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -C.PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = C.PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -C.PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = C.PLAYER_SPEED
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, C.INTERNAL_WIDTH, C.INTERNAL_HEIGHT)

        self.current_room.update(self.player)

        if self.game_map.current_room_coords == (0, 0):
            exit_direction = self.game_map.entry_direction
            should_exit = False
            if exit_direction == "NORTH" and self.player.rect.top <= 0:
                should_exit = True
            elif (
                exit_direction == "SOUTH"
                and self.player.rect.bottom >= C.INTERNAL_HEIGHT
            ):
                should_exit = True
            elif exit_direction == "WEST" and self.player.rect.left <= 0:
                should_exit = True
            elif (
                exit_direction == "EAST" and self.player.rect.right >= C.INTERNAL_WIDTH
            ):
                should_exit = True
            if should_exit:
                self.context.exit_to_overworld_from = "Dungeon"
                self.context.overworld_entry_direction = exit_direction
                self.done = True
                self.next_state = "OVERWORLD"
                return

        new_room = None
        if self.player.rect.right >= C.INTERNAL_WIDTH:
            new_room = self.game_map.move_to_room(dx=1, dy=0)
        elif self.player.rect.left <= 0:
            new_room = self.game_map.move_to_room(dx=-1, dy=0)
        elif self.player.rect.bottom >= C.INTERNAL_HEIGHT:
            new_room = self.game_map.move_to_room(dx=0, dy=1)
        elif self.player.rect.top <= 0:
            new_room = self.game_map.move_to_room(dx=0, dy=-1)
        if new_room:
            if self.player.rect.right >= C.INTERNAL_WIDTH:
                self.player.rect.left = 10
            elif self.player.rect.left <= 0:
                self.player.rect.right = C.INTERNAL_WIDTH - 10
            elif self.player.rect.bottom >= C.INTERNAL_HEIGHT:
                self.player.rect.top = 10
            elif self.player.rect.top <= 0:
                self.player.rect.bottom = C.INTERNAL_HEIGHT - 10
            self.current_room.remove_player(self.player)
            self.current_room = new_room
            self.current_room.add_player(self.player)
            self.game_map.explored_rooms.add(self.game_map.current_room_coords)

        collided_enemies = pygame.sprite.spritecollide(
            self.player, self.current_room.enemies, False
        )
        if collided_enemies:
            self.context.active_enemy = collided_enemies[0]
            self.done = True
            self.next_state = "COMBAT"

    def draw(self, screen):
        screen.fill(C.ROOM_COLOR)
        self.current_room.draw(screen)
        self.draw_hud(screen)
        if self.show_map:
            draw_map(screen, self.game_map)


class CombatState(GameplayState):
    def __init__(self, game):
        super().__init__(game)
        self.current_room = self.game_map.get_current_room()
        self.active_enemy = self.context.active_enemy
        self.combat_log = [f"You encounter a {self.active_enemy.name}!"]
        self.current_turn = "PLAYER"
        self.phase = "ACTIVE"

    def handle_events(self, event):
        super().handle_events(event)
        if self.phase == "VICTORY":
            if event.type == pygame.KEYDOWN:
                self.done = True
                self.next_state = "EXPLORING"
        elif self.phase == "ACTIVE" and self.current_turn == "PLAYER":
            player_action = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player_action = resolve_attack(
                        self.player, self.active_enemy, "normal"
                    )
                elif event.key == pygame.K_2:
                    player_action = resolve_attack(
                        self.player, self.active_enemy, "power"
                    )
                elif event.key == pygame.K_3:
                    self.player.is_defending = True
                    self.combat_log.append(
                        f"{self.player.first_name} takes a defensive stance."
                    )
                    self.current_turn = "ENEMY"
            if player_action:
                self.combat_log.append(player_action["message"])
                damage_dealt = player_action["damage"]
                self.active_enemy.health = max(
                    0, self.active_enemy.health - damage_dealt
                )
                self.current_turn = "ENEMY"

    def drop_chance(self, drop_list: list[dict], template_data):
        """Determines if something drops based on its drop chance."""
        for item in drop_list:
            random_chance = random.random()
            if random_chance < item["drop_chance"]:
                self.player.inventory.append(template_data[item["item_id"]])
                self.combat_log.append(
                    f"You find a {template_data[item['item_id']].name}!"
                )

    def update(self, dt):
        # Don't update logic if the fight is already won
        if self.phase == "VICTORY":
            return
        if self.player.health <= 0:
            self.combat_log.append("You have been defeated!")
            self.done = True
            self.next_state = "GAME_OVER"
            return
        if self.active_enemy.health <= 0:
            # Switch to victory phase instead of ending the state
            self.phase = "VICTORY"
            gold_to_add = random.randint(*self.active_enemy.gold_drop_range)
            self.player.gold += gold_to_add
            self.combat_log.append(
                f"The {self.active_enemy.name} is defeated! You find {gold_to_add} gold on them."
            )
            # Check for item drops
            self.drop_chance(self.active_enemy.item_drops, ITEM_TEMPLATES)

            self.active_enemy.kill()
            if self.current_room.enemies.__len__() == 0:
                # If no enemies left, give more gold for clearing the room
                extra_gold = random.randint(10, 30)
                self.player.gold += extra_gold
                self.combat_log.append(
                    f"You clear the room and find an additional {extra_gold} gold!"
                )
            return
        if self.current_turn == "ENEMY":
            pygame.time.wait(C.COMBAT_ENEMY_TURN_DELAY)
            if self.active_enemy.is_charging_attack:
                attack_result = resolve_attack(
                    self.active_enemy, self.player, "vicious_bite"
                )
                self.active_enemy.is_charging_attack = False
            else:
                if random.randint(1, 100) <= 75:
                    attack_result = resolve_attack(
                        self.active_enemy, self.player, "normal"
                    )
                else:
                    self.active_enemy.is_charging_attack = True
                    attack_result = {
                        "damage": 0,
                        "message": f"The {self.active_enemy.name} growls, preparing a vicious bite!",
                    }
            damage_taken = attack_result["damage"]
            if self.player.is_defending:
                damage_taken = damage_taken // 2
                attack_result["message"] += " (Blocked!)"
                self.player.is_defending = False
            self.combat_log.append(attack_result["message"])
            self.player.health = max(0, self.player.health - damage_taken)
            if not self.active_enemy.is_charging_attack:
                self.current_turn = "PLAYER"

    def draw(self, screen):
        # Draw the exploring view first as a background
        screen.fill(C.ROOM_COLOR)
        self.current_room.draw(screen)
        # Draw combat overlay
        overlay = pygame.Surface((C.INTERNAL_WIDTH, C.INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        # Draw HUD (player and enemy stats)
        self.draw_hud(screen)

        # We need a font for the VICTORY text
        font_title = pygame.font.Font(None, C.FONT_SIZE_TITLE)

        # Only show the enemy health if they are still active
        if self.phase == "ACTIVE":
            enemy_health_text = self.font_text.render(
                f"{self.active_enemy.name} Health: {self.active_enemy.health}",
                True,
                C.RED,
            )
            screen.blit(enemy_health_text, (C.INTERNAL_WIDTH - 250, 20))

        # Combat Log (Bottom-Left)
        log_start_x = 20
        log_start_y = C.INTERNAL_HEIGHT - 150
        line_height = 30
        messages_to_draw = self.combat_log[-4:]
        for i, message in enumerate(messages_to_draw):
            y_pos = log_start_y + i * line_height
            log_text = self.font_text.render(message, True, C.WHITE)
            screen.blit(log_text, (log_start_x, y_pos))

        # Action Menu (Bottom-Right) - only if combat is active
        if self.phase == "ACTIVE" and self.current_turn == "PLAYER":
            menu_x = C.INTERNAL_WIDTH - 250
            menu_y = C.INTERNAL_HEIGHT - 120
            actions = ["[1] Attack", "[2] Power Attack", "[3] Defend"]
            for i, action in enumerate(actions):
                action_text = self.font_text.render(action, True, C.WHITE)
                screen.blit(action_text, (menu_x, menu_y + i * 30))
        if self.phase == "VICTORY":
            victory_text = font_title.render("VICTORY", True, C.GOLD)
            text_rect = victory_text.get_rect(
                center=(C.INTERNAL_WIDTH / 2, C.INTERNAL_HEIGHT / 2 - 50)
            )
            screen.blit(victory_text, text_rect)
            continue_text = self.font_text.render(
                "Press any key to continue...", True, C.WHITE
            )
            continue_rect = continue_text.get_rect(
                center=(C.INTERNAL_WIDTH / 2, C.INTERNAL_HEIGHT / 2 + 10)
            )
            screen.blit(continue_text, continue_rect)


class GameOverState(GameplayState):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.Font(None, C.FONT_SIZE_TITLE)
        self.font_text = pygame.font.Font(None, C.FONT_SIZE_TEXT)

    def handle_events(self, event):
        super().handle_events(event)
        # If any key is pressed, transition back to character creation
        if event.type == pygame.KEYDOWN:
            self.done = True
            self.next_state = "MAIN_MENU"

    def draw(self, screen):
        # Draw a dark overlay, similar to combat
        overlay = pygame.Surface((C.INTERNAL_WIDTH, C.INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        # Display Game Over text
        title_text = self.font_title.render("Your Legacy Ends Here", True, C.WHITE)
        title_rect = title_text.get_rect(
            center=(C.INTERNAL_WIDTH / 2, C.INTERNAL_HEIGHT / 2 - 50)
        )
        screen.blit(title_text, title_rect)

        # Display the fallen hero's name
        hero_name = f"'{self.player.first_name} {self.player.family_name}' has fallen."
        name_text = self.font_text.render(hero_name, True, C.GRAY)
        name_rect = name_text.get_rect(
            center=(C.INTERNAL_WIDTH / 2, C.INTERNAL_HEIGHT / 2 + 10)
        )
        screen.blit(name_text, name_rect)

        # Display instruction to restart
        instr_text = self.font_text.render(
            "Press any key to begin a new legacy.", True, C.WHITE
        )
        instr_rect = instr_text.get_rect(
            center=(C.INTERNAL_WIDTH / 2, C.INTERNAL_HEIGHT - 100)
        )
        screen.blit(instr_text, instr_rect)


class CharacterSheetState(GameplayState):
    def __init__(self, game):
        super().__init__(game)
        self.previous_state = game.state_stack[-1]
        self.sheet_ui = CharacterSheet(game)  # Pass the whole game object

    def handle_events(self, event):
        super().handle_events(event)
        self.sheet_ui.handle_event(event)  # Delegate to UI
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c or event.key == pygame.K_ESCAPE:
                self.game.pop_state()

    def draw(self, screen):
        self.previous_state.draw(screen)
        self.sheet_ui.draw(screen)

    def use_item(self, item_index):
        if 0 <= item_index < len(self.player.inventory):
            item = self.player.inventory[item_index]
            if isinstance(item, Consumable):
                was_used = item.use(self.player)
                if was_used:
                    self.player.inventory.pop(item_index)

    def equip_item(self, item_index):
        if 0 <= item_index < len(self.player.inventory):
            item = self.player.inventory[item_index]
            if isinstance(item, Weapon):
                # Swap with currently equipped weapon
                if self.player.equipped_weapon:
                    self.player.inventory.append(self.player.equipped_weapon)

                self.player.equipped_weapon = item
                self.player.inventory.pop(item_index)


class PauseState(GameplayState):
    def __init__(self, game):
        super().__init__(game)
        self.previous_state = game.state_stack[-1]
        self.menu_ui = PauseMenu(game)

    def handle_events(self, event):
        super().handle_events(event)
        self.menu_ui.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.pop_state()

    def draw(self, screen):
        # Draw the state below it as the background, then the menu on top
        self.previous_state.draw(screen)
        self.menu_ui.draw(screen)


class ShopState(GameplayState):
    """A state for interacting with a vendor."""

    def __init__(self, game, vendor):
        super().__init__(game)
        self.vendor = vendor
        self.previous_state = game.state_stack[-1]

        # Populate vendor's inventory if it's empty
        if not self.vendor.inventory and self.vendor.vendor_id:
            item_ids = VENDOR_INVENTORIES.get(self.vendor.vendor_id, {}).get(
                "inventory", []
            )
            self.vendor.inventory = [ITEM_TEMPLATES[i_id] for i_id in item_ids]

        self.shop_ui = ShopUI(game, self.vendor, self.player)

    def handle_events(self, event):
        super().handle_events(event)
        self.shop_ui.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.pop_state()

    def buy_item(self, item_index):
        """Logic for the player buying an item."""
        item = self.vendor.inventory[item_index]
        if self.player.gold >= item.value:
            self.player.gold -= item.value
            self.player.inventory.append(item)
            self.vendor.inventory.pop(item_index)
            print(f"Bought {item.name}")

    def sell_item(self, item_index):
        """Logic for the player selling an item."""
        item = self.player.inventory[item_index]
        sell_price = item.value // 2  # Sell for half price
        self.player.gold += sell_price
        self.vendor.inventory.append(item)
        self.player.inventory.pop(item_index)
        print(f"Sold {item.name}")

    def draw(self, screen):
        self.previous_state.draw(screen)
        self.shop_ui.draw(screen)


class SettingsState(GameplayState):
    """A state for managing game settings."""

    def __init__(self, game):
        super().__init__(game)
        self.previous_state = game.state_stack[-1]
        self.settings_ui = SettingsMenu(game)

    def handle_events(self, event):
        super().handle_events(event)
        self.settings_ui.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.pop_state()

    def draw(self, screen):
        self.previous_state.draw(screen)
        self.settings_ui.draw(screen)


# A mapping of state names to their respective classes
STATE_MAP = {
    "CHAR_CREATION": CharCreationState,
    "TOWN": TownState,
    "OVERWORLD": OverworldState,
    "EXPLORING": ExploringState,
    "COMBAT": CombatState,
    "GAME_OVER": GameOverState,
    "CHAR_SHEET": CharacterSheetState,
    "PAUSE": PauseState,
    "MAIN_MENU": MainMenuState,
    "SHOP": ShopState,
    "SETTINGS": SettingsState,
}


def create_state(state_name, game, initial_data=None, **kwargs):
    """Factory function to create state instances."""
    state_class = STATE_MAP[state_name]
    if state_name == "CHAR_CREATION":
        return state_class(game, initial_data)
    else:
        # Assumes all other states take the game object
        return state_class(game, **kwargs)
