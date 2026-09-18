"""
Configuration constants and theme settings for the retro Game Boy escape room.
"""
import pygame

# Display settings
WINDOW_WIDTH = 880
WINDOW_HEIGHT = 740
FPS = 60

# Game Boy (DMG-01) 4-Color Palette
COLOR_DARKEST = (15, 56, 15)    # #0f380f (Deepest background/shadows)
COLOR_DARK = (48, 98, 48)       # #306230 (Secondary borders, dim text)
COLOR_LIGHT = (139, 172, 15)    # #8bac0f (Main UI surfaces, active icons)
COLOR_LIGHTEST = (155, 188, 15) # #9bbc0f (Brightest text, highlights, cursor)

# Game Rules & Defaults
DEFAULT_TIME_LIMIT_SECONDS = 60 * 60  # 60 minutes
WRONG_ANSWER_PENALTY_SECONDS = 30     # 30 second penalty for incorrect attempt
CURSOR_BLINK_RATE_MS = 500

# UI Dimensions & Padding
MARGIN = 24
IMAGE_VIEW_WIDTH = 640
IMAGE_VIEW_HEIGHT = 380
BORDER_WIDTH = 3
