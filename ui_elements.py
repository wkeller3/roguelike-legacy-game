# ui_elements.py
import pygame
import constants as C


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
    """A UI element for displaying conversations."""

    def __init__(self):
        self.rect = pygame.Rect(50, C.SCREEN_HEIGHT - 150, C.SCREEN_WIDTH - 100, 120)
        self.font_text = pygame.font.Font(None, C.FONT_SIZE_TEXT)
        self.font_speaker = pygame.font.Font(None, C.FONT_SIZE_HEADER)

        self.is_active = False
        self.speaker_name = ""
        self.dialogue_lines = []
        self.current_line_index = 0

    def start_dialogue(self, npc):
        """Starts a new conversation."""
        self.is_active = True
        self.speaker_name = npc.name
        self.dialogue_lines = npc.dialogue
        self.current_line_index = 0

    def advance(self):
        """Advances to the next line of dialogue, or ends it."""
        self.current_line_index += 1
        if self.current_line_index >= len(self.dialogue_lines):
            self.is_active = False
            self.speaker_name = ""
            self.dialogue_lines = []

    def draw(self, screen):
        if not self.is_active:
            return

        # Draw the main box
        pygame.draw.rect(screen, (10, 10, 20), self.rect)
        pygame.draw.rect(screen, C.WHITE, self.rect, 2)

        # Draw the speaker's name
        speaker_surf = self.font_speaker.render(
            f"{self.speaker_name}:", True, (200, 200, 100)
        )
        screen.blit(speaker_surf, (self.rect.x + 15, self.rect.y + 15))

        # Draw the current line of dialogue
        line_to_show = self.dialogue_lines[self.current_line_index]
        dialogue_surf = self.font_text.render(line_to_show, True, C.WHITE)
        screen.blit(dialogue_surf, (self.rect.x + 20, self.rect.y + 60))
