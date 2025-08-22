# ui_elements.py
import pygame
import constants as C
import os

from item import Consumable, Weapon


def wrap_text(text, font, max_width):
    """Wraps text to a specific width."""
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines


class UIElement:
    def __init__(self, rect):
        self.rect = rect
        self.is_visible = True

    def handle_event(self, event):
        """Base event handler, can be overridden by subclasses."""
        pass

    def draw(self, screen):
        """Base draw method, must be overridden by subclasses."""
        raise NotImplementedError("Each UI element must have its own draw method.")

    def show(self):
        self.is_visible = True

    def hide(self):
        self.is_visible = False


class Button(UIElement):
    """A clickable button UI element."""

    def __init__(self, x, y, width, height, text, font, enabled_color, disabled_color):
        rect = pygame.Rect(x, y, width, height)
        super().__init__(rect)
        self.text = text
        self.font = font
        self.enabled_color = enabled_color
        self.disabled_color = disabled_color
        self.is_disabled = False

    def draw(self, screen):
        """Draws the button on the screen."""
        # Determine color based on state
        color = self.enabled_color if not self.is_disabled else self.disabled_color

        # Draw the button rectangle
        pygame.draw.rect(screen, color, self.rect)

        # Render and center the text
        text_surface = self.font.render(self.text, True, C.BLACK)  # Black text
        text_rect = text_surface.get_rect(center=self.rect.center)

        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """Checks if the button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and not self.is_disabled:
                return True
        return False


class TextBox(UIElement):
    """A simple box for displaying a single line of text."""

    def __init__(self, text, rect, font, text_color=C.WHITE, bg_color=None):
        super().__init__(rect)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.is_visible = True

    def set_text(self, new_text):
        self.text = new_text

    def draw(self, screen):
        if not self.is_visible:
            return

        if self.bg_color:
            pygame.draw.rect(screen, self.bg_color, self.rect)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class DialogueBox(UIElement):
    """A UI element for displaying branching conversations with keyboard and mouse support."""

    def __init__(self):
        rect = pygame.Rect(C.DIALOGUE_BOX_RECT)
        super().__init__(rect)
        self.font_text = pygame.font.Font(None, C.FONT_SIZE_TEXT)
        self.font_speaker = pygame.font.Font(None, C.FONT_SIZE_HEADER)

        self.is_active = False
        self.speaker_name = ""
        self.dialogue_nodes = {}
        self.current_node_key = "start"

        self.choice_rects = []
        self.selected_choice_idx = 0

    def start_dialogue(self, npc):
        """Starts a new conversation with an NPC."""
        self.is_active = True
        self.speaker_name = npc.name
        self.dialogue_nodes = npc.dialogue_nodes
        self.current_node_key = "start"
        self.selected_choice_idx = 0

    def _select_choice(self, choice_index):
        """Processes the selection of a choice."""
        current_node = self.dialogue_nodes.get(self.current_node_key)
        if not current_node or choice_index >= len(current_node["choices"]):
            return

        target_node = current_node["choices"][choice_index]["target"]
        if target_node == "end":
            self.is_active = False  # End conversation
        else:
            self.current_node_key = target_node  # Go to next node
            self.selected_choice_idx = 0  # Reset selection for the new node

    def handle_event(self, event):
        """Handles player input for dialogue choices."""
        if not self.is_active:
            return

        current_node = self.dialogue_nodes.get(self.current_node_key)
        if not current_node:
            return
        num_choices = len(current_node["choices"])

        # Handle Keyboard Input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_choice_idx = (self.selected_choice_idx - 1) % num_choices
            elif event.key == pygame.K_DOWN:
                self.selected_choice_idx = (self.selected_choice_idx + 1) % num_choices
            elif (
                event.key == pygame.K_RETURN
                or event.key == pygame.K_SPACE
                or event.key == pygame.K_e
            ):
                self._select_choice(self.selected_choice_idx)

        # Handle Mouse Click Input
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, choice_rect in enumerate(self.choice_rects):
                if choice_rect.collidepoint(event.pos):
                    self._select_choice(i)
                    return

    def draw(self, screen):
        if not self.is_active:
            return

        current_node = self.dialogue_nodes.get(self.current_node_key)
        if not current_node:
            self.is_active = False
            return

        # Draw the main box
        pygame.draw.rect(screen, (10, 10, 20), self.rect)
        pygame.draw.rect(screen, C.WHITE, self.rect, 2)

        # Draw the speaker's name
        speaker_surf = self.font_speaker.render(
            f"{self.speaker_name}:", True, (200, 200, 100)
        )
        screen.blit(speaker_surf, (self.rect.x + 15, self.rect.y + 10))

        # --- NEW: Text Wrapping for main dialogue text ---
        wrapped_lines = wrap_text(
            current_node["text"], self.font_text, self.rect.width - 40
        )
        for i, line in enumerate(wrapped_lines):
            dialogue_surf = self.font_text.render(line, True, C.WHITE)
            screen.blit(dialogue_surf, (self.rect.x + 20, self.rect.y + 45 + i * 25))

        # --- NEW: Mouse Hover and Keyboard Selection for choices ---
        self.choice_rects = []
        mouse_pos = pygame.mouse.get_pos()
        choice_y_start = self.rect.y + 90
        for i, choice in enumerate(current_node["choices"]):
            # Check for mouse hover to update selection
            temp_rect = pygame.Rect(
                self.rect.x + 25, choice_y_start + i * 25, self.rect.width - 50, 25
            )
            if temp_rect.collidepoint(mouse_pos):
                self.selected_choice_idx = i

            # Determine color based on selection
            color = (
                (200, 200, 255) if i == self.selected_choice_idx else (150, 150, 180)
            )

            choice_text = f"{choice['text']}"  # Removed numbering for a cleaner look
            choice_surf = self.font_text.render(choice_text, True, color)
            choice_pos = (self.rect.x + 30, choice_y_start + i * 25)

            # We store the actual rendered rect for click detection
            rendered_rect = screen.blit(choice_surf, choice_pos)
            self.choice_rects.append(rendered_rect)


class CharacterSheet(UIElement):
    """A UI component that draws all player information and handles inventory interaction."""

    def __init__(self, game):
        rect = pygame.Rect(C.CHAR_SHEET_RECT)
        super().__init__(rect)
        self.game = game
        self.player = game.context.player
        self.font_header = pygame.font.Font(None, C.FONT_SIZE_HEADER)
        self.font_text = pygame.font.Font(None, C.FONT_SIZE_TEXT)

        self.selected_item_idx = 0
        self.inventory_rects = []
        self.equip_button = Button(
            self.rect.x + 300,
            self.rect.bottom - 60,
            120,
            40,
            "Equip",
            self.font_text,
            C.GREEN,
            C.GRAY,
        )
        self.use_button = Button(
            self.rect.x + 430,
            self.rect.bottom - 60,
            120,
            40,
            "Use",
            self.font_text,
            C.BLUE,
            C.GRAY,
        )

    def handle_event(self, event):
        # Handle button clicks
        if self.equip_button.handle_event(event):
            self.game.get_active_state().equip_item(self.selected_item_idx)
        if self.use_button.handle_event(event):
            self.game.get_active_state().use_item(self.selected_item_idx)

        # Handle keyboard navigation for inventory
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item_idx = max(0, self.selected_item_idx - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_item_idx = min(
                    len(self.player.inventory) - 1, self.selected_item_idx + 1
                )

    def draw(self, screen):
        # Draw background panel
        pygame.draw.rect(screen, (30, 30, 40, 230), self.rect)
        pygame.draw.rect(screen, C.WHITE, self.rect, 2)

        # Name
        name_text = self.font_header.render(
            f"{self.player.first_name} {self.player.family_name}", True, C.WHITE
        )
        screen.blit(name_text, (self.rect.x + 20, self.rect.y + 20))

        # Attributes Section (Left Column)
        y_offset = self.rect.y + 80
        stats_header = self.font_header.render("Attributes", True, C.WHITE)
        screen.blit(stats_header, (self.rect.x + 20, y_offset))
        for i, (stat, value) in enumerate(self.player.stats.items()):
            stat_text = self.font_text.render(f"{stat}: {value}", True, C.GRAY)
            screen.blit(stat_text, (self.rect.x + 30, y_offset + 40 + i * 30))

        # Gold Display (Left Column, below Attributes)
        gold_text = self.font_text.render(
            f"Gold: {self.player.gold}", True, (255, 223, 0)
        )
        screen.blit(gold_text, (self.rect.x + 30, y_offset + 40 + 5 * 30))

        # --- Equipped Weapon Section (Right Column) ---
        x_offset = self.rect.x + 300
        y_offset = self.rect.y + 80

        weapon_header = self.font_header.render("Equipped Weapon", True, C.WHITE)
        screen.blit(weapon_header, (x_offset, y_offset))

        if self.player.equipped_weapon:
            weapon = self.player.equipped_weapon
            y_offset += 40

            # Weapon Name
            name_text = self.font_text.render(f"{weapon.name}", True, C.WHITE)
            screen.blit(name_text, (x_offset + 10, y_offset))
            y_offset += 30

            # Weapon Stats
            dmg_text = self.font_text.render(
                f"Damage: {weapon.base_damage[0]}-{weapon.base_damage[1]}", True, C.GRAY
            )
            screen.blit(dmg_text, (x_offset + 10, y_offset))
            y_offset += 30

            crit_text = self.font_text.render(
                f"Crit Chance: {int(weapon.crit_chance * 100)}%", True, C.GRAY
            )
            screen.blit(crit_text, (x_offset + 10, y_offset))
            y_offset += 30

            crit_mult_text = self.font_text.render(
                f"Crit Multiplier: x{weapon.crit_multiplier}", True, C.GRAY
            )
            screen.blit(crit_mult_text, (x_offset + 10, y_offset))
        else:
            # If no weapon is equipped
            no_weapon_text = self.font_text.render("None", True, C.GRAY)
            screen.blit(no_weapon_text, (x_offset + 10, y_offset + 40))

        # --- Interactive Inventory Section ---
        x_offset = self.rect.x + 300
        y_offset = self.rect.y + 280
        inv_header = self.font_header.render("Inventory", True, C.WHITE)
        screen.blit(inv_header, (x_offset, y_offset))
        y_offset += 40

        self.inventory_rects = []
        if not self.player.inventory:
            inv_text = self.font_text.render("Empty", True, C.GRAY)
            screen.blit(inv_text, (x_offset + 10, y_offset))
        else:
            for i, item in enumerate(self.player.inventory):
                color = C.WHITE if i == self.selected_item_idx else C.GRAY
                item_text = self.font_text.render(f"- {item.name}", True, color)
                item_rect = screen.blit(item_text, (x_offset + 10, y_offset))
                self.inventory_rects.append(item_rect)
                y_offset += 30

        # --- Draw Buttons ---
        selected_item = (
            self.player.inventory[self.selected_item_idx]
            if self.player.inventory
            else None
        )
        self.equip_button.is_disabled = not isinstance(selected_item, Weapon)
        self.use_button.is_disabled = not isinstance(selected_item, Consumable)
        self.equip_button.draw(screen)
        self.use_button.draw(screen)


class PauseMenu(UIElement):
    """A UI component for the pause menu."""

    def __init__(self, game):
        rect = pygame.Rect(
            C.INTERNAL_WIDTH / 2 - 150, C.INTERNAL_HEIGHT / 2 - 200, 300, 400
        )
        super().__init__(rect)
        self.game = game
        self.font_title = pygame.font.Font(None, C.FONT_SIZE_TITLE)

        # Create buttons for the menu
        self.resume_button = Button(
            self.rect.x + 50,
            self.rect.y + 80,
            200,
            50,
            "Resume",
            self.font_title,
            C.GREEN,
            C.GRAY,
        )
        self.save_button = Button(
            self.rect.x + 50,
            self.rect.y + 160,
            200,
            50,
            "Save Game",
            self.font_title,
            C.GREEN,
            C.GRAY,
        )
        self.settings_button = Button(
            self.rect.x + 50,
            self.rect.y + 240,
            200,
            50,
            "Settings",
            self.font_title,
            C.GRAY,
            C.GRAY,
        )
        self.quit_button = Button(
            self.rect.x + 50,
            self.rect.y + 320,
            200,
            50,
            "Quit Game",
            self.font_title,
            C.RED,
            C.GRAY,
        )
        self.settings_button.is_disabled = True  # Disable until we implement it

    def handle_event(self, event):
        if self.resume_button.handle_event(event):
            self.game.pop_state()
        if self.save_button.handle_event(event):
            self.game.save_game_data()
            self.game.pop_state()  # Close menu after saving
        if self.quit_button.handle_event(event):
            self.game.running = False

    def draw(self, screen):
        # Draw a semi-transparent background for the whole screen
        overlay = pygame.Surface((C.INTERNAL_WIDTH, C.INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Draw the menu panel
        pygame.draw.rect(screen, (30, 30, 40), self.rect)
        pygame.draw.rect(screen, C.WHITE, self.rect, 2)

        # Draw title
        title_text = self.font_title.render("Paused", True, C.WHITE)
        title_rect = title_text.get_rect(centerx=self.rect.centerx, y=self.rect.y + 20)
        screen.blit(title_text, title_rect)

        # Draw buttons
        self.resume_button.draw(screen)
        self.save_button.draw(screen)
        self.settings_button.draw(screen)
        self.quit_button.draw(screen)


class MainMenu(UIElement):
    """A UI component for the main menu."""

    def __init__(self, game):
        rect = pygame.Rect(0, 0, C.INTERNAL_WIDTH, C.INTERNAL_HEIGHT)
        super().__init__(rect)
        self.game = game
        self.font_title = pygame.font.Font(None, C.FONT_SIZE_TITLE + 20)
        self.font_button = pygame.font.Font(None, C.FONT_SIZE_TITLE)

        self.new_game_button = Button(
            self.rect.centerx - 150,
            self.rect.y + 250,
            300,
            60,
            "New Legacy",
            self.font_button,
            C.GREEN,
            C.GRAY,
        )
        self.load_game_button = Button(
            self.rect.centerx - 150,
            self.rect.y + 330,
            300,
            60,
            "Load Legacy",
            self.font_button,
            C.GREEN,
            C.GRAY,
        )

        # Disable the load button if no save file exists
        if not os.path.exists("savegame.json"):
            self.load_game_button.is_disabled = True

    def handle_event(self, event):
        if self.new_game_button.handle_event(event):
            self.game.get_active_state().next_state = "CHAR_CREATION"
            self.game.get_active_state().done = True

        if self.load_game_button.handle_event(event):
            self.game.load_and_start_from_save()

    def draw(self, screen):
        title_text = self.font_title.render("Legacy of the Cursed", True, C.WHITE)
        title_rect = title_text.get_rect(centerx=self.rect.centerx, y=self.rect.y + 100)
        screen.blit(title_text, title_rect)

        self.new_game_button.draw(screen)
        self.load_game_button.draw(screen)


class ShopUI(UIElement):
    """A UI component for the shop/vendor screen."""

    def __init__(self, game, vendor, player):
        rect = pygame.Rect(50, 50, C.INTERNAL_WIDTH - 100, C.INTERNAL_HEIGHT - 100)
        super().__init__(rect)
        self.game = game
        self.vendor = vendor
        self.player = player
        self.font_header = pygame.font.Font(None, C.FONT_SIZE_HEADER)
        self.font_text = pygame.font.Font(None, C.FONT_SIZE_TEXT)
        self.buy_buttons = []
        self.sell_buttons = []

    def handle_event(self, event):
        for i, button in enumerate(self.buy_buttons):
            if button.handle_event(event):
                self.game.get_active_state().buy_item(i)
                return  # Prevent multiple actions in one click

        for i, button in enumerate(self.sell_buttons):
            if button.handle_event(event):
                self.game.get_active_state().sell_item(i)
                return

    def draw(self, screen):
        # Draw a background for the whole screen
        overlay = pygame.Surface((C.INTERNAL_WIDTH, C.INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Draw the main panel
        pygame.draw.rect(screen, (30, 30, 40), self.rect)
        pygame.draw.rect(screen, C.WHITE, self.rect, 2)

        # --- Vendor's Inventory ---
        vendor_header = self.font_header.render(
            f"{self.vendor.name}'s Wares", True, C.WHITE
        )
        screen.blit(vendor_header, (self.rect.x + 20, self.rect.y + 20))
        self.buy_buttons = []
        y_offset = self.rect.y + 70
        for i, item in enumerate(self.vendor.inventory):
            item_text = self.font_text.render(
                f"{item.name} ({item.value}g)", True, C.WHITE
            )
            screen.blit(item_text, (self.rect.x + 20, y_offset))

            buy_button = Button(
                self.rect.x + 250,
                y_offset - 5,
                80,
                30,
                "Buy",
                self.font_text,
                C.GREEN,
                C.GRAY,
            )
            if self.player.gold < item.value:
                buy_button.is_disabled = True
            self.buy_buttons.append(buy_button)
            buy_button.draw(screen)
            y_offset += 40

        # --- Player's Inventory ---
        player_header = self.font_header.render("Your Inventory", True, C.WHITE)
        screen.blit(player_header, (self.rect.centerx + 20, self.rect.y + 20))
        player_gold = self.font_text.render(f"Gold: {self.player.gold}", True, C.GOLD)
        screen.blit(player_gold, (self.rect.centerx + 20, self.rect.y + 50))

        self.sell_buttons = []
        y_offset = self.rect.y + 100
        for i, item in enumerate(self.player.inventory):
            item_text = self.font_text.render(
                f"{item.name} ({item.value // 2}g)", True, C.WHITE
            )  # Sell for half price
            screen.blit(item_text, (self.rect.centerx + 20, y_offset))

            sell_button = Button(
                self.rect.centerx + 250,
                y_offset - 5,
                80,
                30,
                "Sell",
                self.font_text,
                C.YELLOW,
                C.GRAY,
            )
            self.sell_buttons.append(sell_button)
            sell_button.draw(screen)
            y_offset += 40
