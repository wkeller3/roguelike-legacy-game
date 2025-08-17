# states.py

import pygame
import random
import constants as C
from hero import Hero
from npc import NPC
from gamemap import GameMap
from combat import resolve_attack
from map_view import draw_map
from room import Room
import json
from ui_elements import Button, TextBox, DialogueBox, CharacterSheet


class BaseState:
    """
    A base class for all game states. It provides a standard interface
    for handling events, updating logic, and drawing to the screen.
    """

    def __init__(self, game, persistent_data):
        self.game = game
        self.persistent_data = persistent_data
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
    """
    The state for creating a new character. Handles name input, stat allocation,
    and weapon selection.
    """

    def __init__(self, game, char_creation_data):
        super().__init__(game, {})
        self.data = char_creation_data
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
                pos_y=C.SCREEN_HEIGHT / 2,
            )
            player.stats = self.data["stats"]
            player.equipped_weapon = self.data["weapon_choices"][
                self.data["selected_weapon_idx"]
            ]
            game_map = GameMap(
                max_rooms=15, screen_width=C.SCREEN_WIDTH, screen_height=C.SCREEN_HEIGHT
            )
            self.persistent_data["player"] = player
            self.persistent_data["game_map"] = game_map
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
            elif len(self.data["name"]) < 15:
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
        screen.blit(title_text, (C.SCREEN_WIDTH / 2 - title_text.get_width() / 2, 20))
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


class GameplayState(BaseState):
    """
    An intermediate class for states that share the main gameplay data
    (player, map, etc.), to avoid code duplication.
    """

    def __init__(self, game, persistent_data):
        super().__init__(game, persistent_data)
        self.player = self.persistent_data.get("player")
        self.game_map = self.persistent_data.get("game_map")
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
        gold_text = self.font_text.render(
            f"Gold: {self.player.gold}", True, (255, 223, 0)
        )
        screen.blit(gold_text, (20, y_offset))


class TownState(GameplayState):
    """
    The state for the main town or hub area. It's a safe zone
    with no enemies, and now with interactable NPCs.
    """

    def __init__(self, game, persistent_data):
        super().__init__(game, persistent_data)
        self.town_room = Room(C.SCREEN_WIDTH, C.SCREEN_HEIGHT, room_type="town")
        self.town_room.add_player(self.player)

        # --- Load NPCs from the data file ---
        self._load_npcs()

        # Player repositioning logic
        entry_point = self.persistent_data.get("entry_direction", "CENTER")
        if entry_point == "NORTH":
            self.player.rect.midtop = (C.SCREEN_WIDTH / 2, 20)
        elif entry_point == "SOUTH":
            self.player.rect.midbottom = (C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT - 20)
        elif entry_point == "WEST":
            self.player.rect.midleft = (20, C.SCREEN_HEIGHT / 2)
        elif entry_point == "EAST":
            self.player.rect.midright = (C.SCREEN_WIDTH - 20, C.SCREEN_HEIGHT / 2)
        else:
            self.player.rect.center = (C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2)

        # --- Dialogue System variables ---
        self.is_in_dialogue = False
        self.nearby_npc = None
        self.active_dialogue = []
        self.dialogue_index = 0
        self.active_npc = None

        # --- Create instances of our UI elements ---
        hint_rect = pygame.Rect(0, C.SCREEN_HEIGHT - 60, C.SCREEN_WIDTH, 50)
        self.interaction_hint = TextBox("", hint_rect, self.font_text)
        self.interaction_hint.is_visible = False
        self.dialogue_box = DialogueBox()

    def _load_npcs(self):
        """Loads NPC data from the JSON file and populates the town."""
        with open("npcs.json", "r") as f:
            all_npc_data = json.load(f)

        # Get the list of NPCs specifically for the "Town" location
        town_npcs = all_npc_data.get("Town", [])

        for npc_data in town_npcs:
            # Create an NPC instance from the template data
            npc = NPC(template_data=npc_data)
            self.town_room.add_npc(npc)

    def handle_events(self, event):
        super().handle_events(event)
        # --- Delegate event handling to the DialogueBox ---
        if self.dialogue_box.is_active:
            self.dialogue_box.handle_event(event)
            return  # Don't process other keys while in dialogue

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:  # The 'Interact' key
                if self.nearby_npc:
                    # Start dialogue if not already active
                    self.dialogue_box.start_dialogue(self.nearby_npc)
            if event.key == pygame.K_c:
                self.game.push_state("CHAR_SHEET")

    def update(self, dt):
        # --- Pause player movement and exits during dialogue ---
        if self.dialogue_box.is_active:
            return
        player_speed = 5
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = player_speed
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, C.SCREEN_WIDTH, C.SCREEN_HEIGHT)

        # --- Check for nearby NPCs instead of just collision ---
        self.nearby_npc = None  # Reset each frame
        for npc in self.town_room.npcs:
            # Check distance between player and NPC centers
            distance = pygame.math.Vector2(self.player.rect.center).distance_to(
                npc.rect.center
            )
            if distance < 60:  # Interaction radius of 60 pixels
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
        elif self.player.rect.bottom >= C.SCREEN_HEIGHT:
            exit_direction = "SOUTH"
        elif self.player.rect.left <= 0:
            exit_direction = "WEST"
        elif self.player.rect.right >= C.SCREEN_WIDTH:
            exit_direction = "EAST"

        if exit_direction:
            self.persistent_data["exit_to_overworld_from"] = "Town"
            self.persistent_data["overworld_entry_direction"] = exit_direction
            self.done = True
            self.next_state = "OVERWORLD"

    def draw(self, screen):
        screen.fill(C.ROOM_COLOR)
        self.town_room.draw(screen)
        self.draw_hud(screen)
        # Draw the UI elements
        self.interaction_hint.draw(screen)
        self.dialogue_box.draw(screen)


class OverworldState(GameplayState):
    def __init__(self, game, persistent_data):
        super().__init__(game, persistent_data)

        self.pois = {
            "Town": {"rect": pygame.Rect(180, 280, 100, 80), "target_state": "TOWN"},
            "Dungeon": {
                "rect": pygame.Rect(520, 280, 100, 80),
                "target_state": "EXPLORING",
            },
        }
        self.player_avatar = pygame.Rect(0, 0, 20, 20)

        # --- Position avatar dynamically based on exit information ---
        exit_location = self.persistent_data.get("exit_to_overworld_from", "Town")
        entry_direction = self.persistent_data.get("overworld_entry_direction", "SOUTH")

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
        player_speed = 5
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = player_speed
        if dx != 0 or dy != 0:
            self.player_avatar.move_ip(dx, dy)
        # --- Dynamic entry direction logic ---
        for name, data in self.pois.items():
            if self.player_avatar.colliderect(data["rect"]):
                if name == "Dungeon":
                    self.persistent_data["entry_direction"] = "WEST"
                else:
                    # Calculate the difference vector between centers
                    dx = self.player_avatar.centerx - data["rect"].centerx
                    dy = self.player_avatar.centery - data["rect"].centery

                    # Determine primary axis of collision
                    if abs(dx) > abs(dy):  # Horizontal collision
                        if dx > 0:
                            self.persistent_data["entry_direction"] = "EAST"
                        else:
                            self.persistent_data["entry_direction"] = "WEST"
                    else:  # Vertical collision
                        if dy > 0:
                            self.persistent_data["entry_direction"] = "SOUTH"
                        else:
                            self.persistent_data["entry_direction"] = "NORTH"
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
    """The state for exploring the dungeon, moving between rooms."""

    def __init__(self, game, persistent_data):
        super().__init__(game, persistent_data)
        self.current_room = self.game_map.get_current_room()
        self.current_room.add_player(self.player)
        self.show_map = False
        # Reposition player based on how they entered the dungeon
        entry_point = self.persistent_data.get("entry_direction")
        if entry_point:
            # If it exists, position the player accordingly
            if entry_point == "NORTH":
                self.player.rect.midtop = (C.SCREEN_WIDTH / 2, 20)
            elif entry_point == "SOUTH":
                self.player.rect.midbottom = (C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT - 20)
            elif entry_point == "WEST":
                self.player.rect.midleft = (20, C.SCREEN_HEIGHT / 2)
            elif entry_point == "EAST":
                self.player.rect.midright = (C.SCREEN_WIDTH - 20, C.SCREEN_HEIGHT / 2)
            # Now, remove the key so this logic doesn't run again after a battle
            del self.persistent_data["entry_direction"]

    def handle_events(self, event):
        super().handle_events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.show_map = not self.show_map
            elif event.key == pygame.K_c:  # 'C' for Character
                self.game.push_state("CHAR_SHEET")

    def update(self, dt):
        if self.show_map:
            return  # Pause game when map is open
        # Player movement
        player_speed = 5
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = player_speed
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, C.SCREEN_WIDTH, C.SCREEN_HEIGHT)
        # Update enemy AI and check for room transitions
        self.current_room.update(self.player)
        # --- Re-structured transition logic ---
        # First, check for the single, specific exit to the overworld
        if self.game_map.current_room_coords == (0, 0) and self.player.rect.left <= 0:
            self.persistent_data["exit_to_overworld_from"] = "Dungeon"
            self.persistent_data["overworld_entry_direction"] = "WEST"
            self.done = True
            self.next_state = "OVERWORLD"
            return  # Exit the update method to prevent other checks

        # If not exiting to overworld, check for room-to-room transitions
        new_room = None
        if self.player.rect.right >= C.SCREEN_WIDTH:
            new_room = self.game_map.move_to_room(dx=1, dy=0)
        elif self.player.rect.left <= 0:
            new_room = self.game_map.move_to_room(dx=-1, dy=0)
        elif self.player.rect.bottom >= C.SCREEN_HEIGHT:
            new_room = self.game_map.move_to_room(dx=0, dy=1)
        elif self.player.rect.top <= 0:
            new_room = self.game_map.move_to_room(dx=0, dy=-1)

        if new_room:
            if self.player.rect.right >= C.SCREEN_WIDTH:
                self.player.rect.left = 10
            elif self.player.rect.left <= 0:
                self.player.rect.right = C.SCREEN_WIDTH - 10
            elif self.player.rect.bottom >= C.SCREEN_HEIGHT:
                self.player.rect.top = 10
            elif self.player.rect.top <= 0:
                self.player.rect.bottom = C.SCREEN_HEIGHT - 10
            self.current_room.remove_player(self.player)
            self.current_room = new_room
            self.current_room.add_player(self.player)
            self.game_map.explored_rooms.add(self.game_map.current_room_coords)

        # Finally, check for combat
        collided_enemies = pygame.sprite.spritecollide(
            self.player, self.current_room.enemies, False
        )
        if collided_enemies:
            self.persistent_data["active_enemy"] = collided_enemies[0]
            self.done = True
            self.next_state = "COMBAT"

    def draw(self, screen):
        screen.fill(C.ROOM_COLOR)
        self.current_room.draw(screen)
        self.draw_hud(screen)
        if self.show_map:
            draw_map(screen, self.game_map)


class CombatState(GameplayState):
    """The state for turn-based combat."""

    def __init__(self, game, persistent_data):
        super().__init__(game, persistent_data)
        self.current_room = self.game_map.get_current_room()
        self.active_enemy = self.persistent_data["active_enemy"]
        self.combat_log = [f"You encounter an Enemy!"]
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
                # Clamp enemy health at 0
                damage_dealt = player_action["damage"]
                self.active_enemy.health = max(
                    0, self.active_enemy.health - damage_dealt
                )
                self.current_turn = "ENEMY"

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
                f"The {self.active_enemy.name} is defeated! You find {gold_to_add} gold."
            )
            self.active_enemy.kill()
            return

        if self.current_turn == "ENEMY":
            pygame.time.wait(500)
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
            # Clamp player health at 0
            self.player.health = max(0, self.player.health - damage_taken)

            if not self.active_enemy.is_charging_attack:
                self.current_turn = "PLAYER"

    def draw(self, screen):
        # Draw the exploring view first as a background
        screen.fill(C.ROOM_COLOR)
        self.current_room.draw(screen)
        # Draw combat overlay
        overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
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
            screen.blit(enemy_health_text, (C.SCREEN_WIDTH - 250, 20))

        # Combat Log (Bottom-Left)
        log_start_x = 20
        log_start_y = C.SCREEN_HEIGHT - 150
        line_height = 30
        messages_to_draw = self.combat_log[-4:]
        for i, message in enumerate(messages_to_draw):
            y_pos = log_start_y + i * line_height
            log_text = self.font_text.render(message, True, C.WHITE)
            screen.blit(log_text, (log_start_x, y_pos))

        # Action Menu (Bottom-Right) - only if combat is active
        if self.phase == "ACTIVE" and self.current_turn == "PLAYER":
            menu_x = C.SCREEN_WIDTH - 250
            menu_y = C.SCREEN_HEIGHT - 120
            actions = ["[1] Attack", "[2] Power Attack", "[3] Defend"]
            for i, action in enumerate(actions):
                action_text = self.font_text.render(action, True, C.WHITE)
                screen.blit(action_text, (menu_x, menu_y + i * 30))

        # --- NEW: Victory Message ---
        if self.phase == "VICTORY":
            victory_text = font_title.render("VICTORY", True, (255, 223, 0))
            text_rect = victory_text.get_rect(
                center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2 - 50)
            )
            screen.blit(victory_text, text_rect)

            continue_text = self.font_text.render(
                "Press any key to continue...", True, C.WHITE
            )
            continue_rect = continue_text.get_rect(
                center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2 + 10)
            )
            screen.blit(continue_text, continue_rect)


class GameOverState(GameplayState):
    """
    A state that is shown when the player's health reaches zero.
    """

    def __init__(self, game, persistent_data):
        super().__init__(game, persistent_data)
        self.font_title = pygame.font.Font(None, C.FONT_SIZE_TITLE)
        self.font_text = pygame.font.Font(None, C.FONT_SIZE_TEXT)

    def handle_events(self, event):
        super().handle_events(event)
        # If any key is pressed, transition back to character creation
        if event.type == pygame.KEYDOWN:
            self.done = True
            # We don't pass any persistent data, starting a fresh run
            self.persistent_data = {}
            self.next_state = "CHAR_CREATION"

    def draw(self, screen):
        # Draw a dark overlay, similar to combat
        overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        # Display Game Over text
        title_text = self.font_title.render("Your Legacy Ends Here", True, C.WHITE)
        title_rect = title_text.get_rect(
            center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2 - 50)
        )
        screen.blit(title_text, title_rect)

        # Display the fallen hero's name
        hero_name = f"'{self.player.first_name} {self.player.family_name}' has fallen."
        name_text = self.font_text.render(hero_name, True, C.GRAY)
        name_rect = name_text.get_rect(
            center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2 + 10)
        )
        screen.blit(name_text, name_rect)

        # Display instruction to restart
        instr_text = self.font_text.render(
            "Press any key to begin a new legacy.", True, C.WHITE
        )
        instr_rect = instr_text.get_rect(
            center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT - 100)
        )
        screen.blit(instr_text, instr_rect)


class CharacterSheetState(GameplayState):
    """A pause state that displays detailed player information."""

    def __init__(self, game, persistent_data):
        super().__init__(game, persistent_data)
        # The previous state, which will be the background
        self.previous_state = game.state_stack[-1]
        self.sheet_ui = CharacterSheet(self.player)

    def handle_events(self, event):
        super().handle_events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c or event.key == pygame.K_ESCAPE:
                self.game.pop_state()

    def draw(self, screen):
        # Draw the state below it in the stack as the background
        self.previous_state.draw(screen)
        # Draw the character sheet on top
        self.sheet_ui.draw(screen)
