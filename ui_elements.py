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
