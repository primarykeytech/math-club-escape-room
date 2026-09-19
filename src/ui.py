"""
Retro UI components, borders, panels, and text rendering for the Game Boy escape room.
"""
import pygame
from src.config import (
    COLOR_DARKEST,
    COLOR_DARK,
    COLOR_LIGHT,
    COLOR_LIGHTEST,
    BORDER_WIDTH
)

class RetroUI:
    def __init__(self):
        pygame.font.init()
        # Find best monospace retro font available on system
        font_candidates = ["consolas", "lucidaconsole", "couriernew", "monospace"]
        self.font_title = pygame.font.SysFont(font_candidates, 24, bold=True)
        self.font_body = pygame.font.SysFont(font_candidates, 18, bold=False)
        self.font_body_bold = pygame.font.SysFont(font_candidates, 18, bold=True)
        self.font_small = pygame.font.SysFont(font_candidates, 14, bold=False)
        self.font_hud = pygame.font.SysFont(font_candidates, 20, bold=True)

    def draw_gb_panel(self, surface: pygame.Surface, rect: pygame.Rect, bg_color=COLOR_DARKEST, border_color=COLOR_LIGHT):
        """Draw an authentic Game Boy styled double-beveled panel with notched corners."""
        # Main fill
        pygame.draw.rect(surface, bg_color, rect)

        # Outer border
        pygame.draw.rect(surface, border_color, rect, width=2)

        # Inner border inset by 3px
        inner_rect = rect.inflate(-6, -6)
        if inner_rect.width > 0 and inner_rect.height > 0:
            pygame.draw.rect(surface, COLOR_DARK, inner_rect, width=1)

        # Corner pixel accents (retro cutout effect)
        corners = [
            (rect.left, rect.top),
            (rect.right - 1, rect.top),
            (rect.left, rect.bottom - 1),
            (rect.right - 1, rect.bottom - 1)
        ]
        for cx, cy in corners:
            surface.set_at((cx, cy), bg_color)

    def draw_text_wrapped(self, surface: pygame.Surface, text: str, rect: pygame.Rect, font: pygame.font.Font, color=COLOR_LIGHTEST, line_spacing=4) -> int:
        """Render text wrapped within a bounding rect (supporting newlines) and return total rendered height."""
        paragraphs = text.split('\n')
        lines = []

        for p in paragraphs:
            if not p.strip():
                lines.append("")
                continue
            words = p.split(' ')
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                w, _ = font.size(test_line)
                if w <= rect.width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                        current_line = []
            if current_line:
                lines.append(' '.join(current_line))

        y = rect.top
        font_height = font.get_linesize()
        for line in lines:
            if y + font_height > rect.bottom:
                break
            if line:
                rendered = font.render(line, True, color)
                surface.blit(rendered, (rect.left, y))
            y += font_height + line_spacing
        return y - rect.top

    def draw_scanlines(self, surface: pygame.Surface, step: int = 4, alpha: int = 35):
        """Draw authentic subtle CRT / LCD scanlines."""
        w, h = surface.get_size()
        scanline_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = (*COLOR_DARKEST, alpha)
        for y in range(0, h, step):
            pygame.draw.line(scanline_surf, color, (0, y), (w, y))
        surface.blit(scanline_surf, (0, 0))
