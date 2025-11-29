import pygame
from enum import Enum

# Window and Board
WINDOW_WIDTH = 1366
WINDOW_HEIGHT = 850
BOARD_SIZE = 6
CELL_SIZE = 96
BOARD_START_X = 400
BOARD_START_Y = 150

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
ORANGE = (255, 165, 0)
NAVY = (25, 25, 112)
LIGHT_BLUE = (38, 196, 249)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Assets Paths
KITTEN_O_SPRITE = "./assets/sprites/kitten-o.png"
CAT_O_SPRITE = "./assets/sprites/cat-o.png"
KITTEN_B_SPRITE = "./assets/sprites/kitten-b.png"
CAT_B_SPRITE = "./assets/sprites/cat-b.png"

KITTEN_MEOW_SOUND = "./assets/sounds/kitten-meow.wav"
CAT_MEOW_SOUND = "./assets/sounds/cat-meow.wav"
BOOP_SOUND = "./assets/sounds/boop.wav"
CHEER_SOUND = "./assets/sounds/cheering.wav"