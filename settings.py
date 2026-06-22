# settings.py - Konfigurasi game

import os

# ========== UKURAN GRID ==========
GRID_WIDTH = 15
GRID_HEIGHT = 15

# CELL_SIZE 50 biar gambar keliatan jelas (Rekomendasi!)
CELL_SIZE = 50

# Ukuran layar (otomatis)
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE   # 750px
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + 150  # 750 + 150 = 900px

# ========== FPS ==========
FPS = 60

# ========== WARNA (Fallback kalau gambar gak ada) ==========
BLACK = (10, 10, 20)
WHITE = (245, 245, 255)
RED = (255, 80, 80)
GREEN = (80, 255, 120)
BLUE = (80, 150, 255)
PURPLE = (160, 80, 255)
ORANGE = (255, 160, 80)
DARK_RED = (180, 40, 40)
GRAY = (80, 80, 100)
DARK_GRAY = (30, 30, 45)
LIGHT_GRAY = (150, 150, 180)
GLOW = (100, 100, 200)

# ========== PATH ASSET ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")