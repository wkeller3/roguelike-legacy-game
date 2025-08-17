# ui_elements.py
import pygame
import constants as C


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


class Button:
    """A clickable button UI element."""

    def __init__(self, x, y, width, height, text, font, enabled_color, disabled_color):
        self.rect = pygame.Rect(x, y, width, height)
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


class TextBox:
    """A simple box for displaying a single line of text."""

    def __init__(self, text, rect, font, text_color=C.WHITE, bg_color=None):
        self.text = text
        self.rect = rect
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


class DialogueBox:
    """A UI element for displaying branching conversations with keyboard and mouse support."""

    def __init__(self):
        self.rect = pygame.Rect(50, C.SCREEN_HEIGHT - 170, C.SCREEN_WIDTH - 100, 150)
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


class CharacterSheet:
    """A UI component that draws all player information."""

    def __init__(self, player):
        self.player = player
        self.font_header = pygame.font.Font(None, C.FONT_SIZE_HEADER)
        self.font_text = pygame.font.Font(None, C.FONT_SIZE_TEXT)
        self.rect = pygame.Rect(100, 50, C.SCREEN_WIDTH - 200, C.SCREEN_HEIGHT - 100)

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

        # --- Inventory Section (Right Column, moved down) ---
        y_offset = self.rect.y + 280  # Adjusted y-position
        inv_header = self.font_header.render("Inventory", True, C.WHITE)
        screen.blit(inv_header, (x_offset, y_offset))
        inv_text = self.font_text.render("Empty", True, C.GRAY)
        screen.blit(inv_text, (x_offset + 10, y_offset + 40))
