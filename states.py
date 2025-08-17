# states.py

import pygame
import random
import constants as C
from hero import Hero
from gamemap import GameMap
from combat import resolve_attack
from map_view import draw_map
from ui_elements import Button


class BaseState:
    """
    A base class for all game states. It provides a standard interface
    for handling events, updating logic, and drawing to the screen.
    """

    def __init__(self):
        self.done = False
        self.quit = False
        self.next_state = None
        self.persistent_data = {}

    def handle_events(self, event):
        """Handle a single user event. Called for each event in the event queue."""
        if event.type == pygame.QUIT:
            self.quit = True

    def update(self, dt):
        """Update game logic for a single frame."""
        pass

    def draw(self, screen):
        """Draw everything to the screen for a single frame."""
        pass


class CharCreationState(BaseState):
    """
    The state for creating a new character. Handles name input, stat allocation,
    and weapon selection.
    """

    def __init__(self, char_creation_data):
        super().__init__()
        self.data = char_creation_data
        self.font_title = pygame.font.Font(None, 48)
        self.font_header = pygame.font.Font(None, 36)
        self.font_text = pygame.font.Font(None, 28)

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
            self.done = True  # Signal to the main loop we are done
            self.next_state = "EXPLORING"

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

    def __init__(self, persistent_data):
        super().__init__()
        self.persistent_data = persistent_data
        self.player = self.persistent_data["player"]
        self.game_map = self.persistent_data["game_map"]
        self.font_text = pygame.font.Font(None, 28)

    def draw_hud(self, screen):
        """Draws the common Heads-Up Display."""
        y_offset = 20
        health_color = C.GREEN if not self.player.is_defending else (100, 200, 255)
        screen.blit(
            self.font_text.render(
                f"Health: {self.player.health}/{self.player.max_health}",
                True,
                health_color,
            ),
            (20, y_offset),
        )
        y_offset += 25
        screen.blit(self.font_text.render("Stats:", True, C.GRAY), (20, y_offset))
        for stat, value in self.player.stats.items():
            y_offset += 25
            screen.blit(
                self.font_text.render(f"- {stat}: {value}", True, C.WHITE),
                (30, y_offset),
            )


class ExploringState(GameplayState):
    """The state for exploring the dungeon, moving between rooms."""

    def __init__(self, persistent_data):
        super().__init__(persistent_data)
        self.current_room = self.game_map.get_current_room()
        self.current_room.add_player(self.player)
        self.show_map = False

    def handle_events(self, event):
        super().handle_events(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self.show_map = not self.show_map

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

        # Check for combat collision
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

    def __init__(self, persistent_data):
        super().__init__(persistent_data)
        self.current_room = self.game_map.get_current_room()
        self.active_enemy = self.persistent_data["active_enemy"]
        self.combat_log = [f"You encounter an Enemy!"]
        self.current_turn = "PLAYER"

    def handle_events(self, event):
        super().handle_events(event)
        if self.current_turn == "PLAYER":
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
                self.active_enemy.health -= player_action["damage"]
                self.current_turn = "ENEMY"

    def update(self, dt):
        if self.player.health <= 0:
            self.combat_log.append("You have been defeated!")
            # For now, just quits. Could transition to a "GameOverState"
            self.done = True
            self.next_state = "GAME_OVER"
            return

        if self.active_enemy.health <= 0:
            self.combat_log.append("Enemy defeated!")
            self.active_enemy.kill()
            self.done = True
            self.next_state = "EXPLORING"
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
                        "message": "The Goblin growls, preparing a vicious bite!",
                    }

            damage_taken = attack_result["damage"]
            if self.player.is_defending:
                damage_taken = damage_taken // 2
                attack_result["message"] += " (Blocked!)"
                self.player.is_defending = False

            self.combat_log.append(attack_result["message"])
            self.player.health -= damage_taken

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
        enemy_health_text = self.font_text.render(
            f"Enemy Health: {self.active_enemy.health}", True, C.RED
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

        # Action Menu (Bottom-Right)
        if self.current_turn == "PLAYER":
            menu_x = C.SCREEN_WIDTH - 250
            menu_y = C.SCREEN_HEIGHT - 120
            actions = ["[1] Attack", "[2] Power Attack", "[3] Defend"]
            for i, action in enumerate(actions):
                action_text = self.font_text.render(action, True, C.WHITE)
                screen.blit(action_text, (menu_x, menu_y + i * 30))


class GameOverState(GameplayState):
    """
    A state that is shown when the player's health reaches zero.
    """

    def __init__(self, persistent_data):
        super().__init__(persistent_data)
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
