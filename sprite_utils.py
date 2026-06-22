# sprite_utils.py - Helper load sprite (support subfolder)

import pygame
import os
from settings import IMAGES_DIR, CELL_SIZE

def load_sprite(filename, default_color, shape="rect", default_emoji=None):
    try:
        full_path = os.path.join(IMAGES_DIR, filename)
        img = pygame.image.load(full_path).convert_alpha()
        # 🔥 PAKSA RESIZE ke CELL_SIZE - 10 biar nge-pas!
        img = pygame.transform.scale(img, (CELL_SIZE - 10, CELL_SIZE - 10))
        return img
    except:
        # Fallback: buat bentuk sendiri
        img = pygame.Surface((CELL_SIZE - 10, CELL_SIZE - 10), pygame.SRCALPHA)
        
        if shape == "rect":
            pygame.draw.rect(img, default_color, img.get_rect(), border_radius=8)
        elif shape == "circle":
            pygame.draw.circle(img, default_color, 
                             (CELL_SIZE//2 - 5, CELL_SIZE//2 - 5), 
                             CELL_SIZE//3)
        elif shape == "diamond":
            points = [
                (CELL_SIZE//2 - 5, 0),
                (CELL_SIZE - 10, CELL_SIZE//2 - 5),
                (CELL_SIZE//2 - 5, CELL_SIZE - 10),
                (0, CELL_SIZE//2 - 5)
            ]
            pygame.draw.polygon(img, default_color, points)
        
        # Tambah emoji di tengah
        if default_emoji:
            font = pygame.font.Font(None, CELL_SIZE // 2)
            emoji_surf = font.render(default_emoji, True, (255, 255, 255))
            emoji_rect = emoji_surf.get_rect(center=(CELL_SIZE//2 - 5, CELL_SIZE//2 - 5))
            img.blit(emoji_surf, emoji_rect)
        
        return img
    
def load_wall_texture():
    """Load wall texture dengan ukuran PAS CELL_SIZE (tanpa padding)"""
    try:
        full_path = os.path.join(IMAGES_DIR, "wall.png")
        img = pygame.image.load(full_path).convert()
        # PAKSA ukuran ke CELL_SIZE x CELL_SIZE
        img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        return img
    except:
        # Fallback: kotak abu-abu dengan border
        img = pygame.Surface((CELL_SIZE, CELL_SIZE))
        img.fill(DARK_GRAY)
        pygame.draw.rect(img, BLACK, img.get_rect(), 2)
        # Tanda X
        pygame.draw.line(img, BLACK, (5, 5), (CELL_SIZE-5, CELL_SIZE-5), 2)
        pygame.draw.line(img, BLACK, (CELL_SIZE-5, 5), (5, CELL_SIZE-5), 2)
        return img