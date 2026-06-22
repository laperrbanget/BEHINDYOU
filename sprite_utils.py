# sprite_utils.py - Helper untuk load sprite (dengan fallback ke bentuk geometris)

import pygame
import os
from settings import IMAGES_DIR, CELL_SIZE

def load_sprite(filename, default_color, shape="rect", default_emoji=None):
    """
    Load gambar dari file. Kalau gak ada, bikin bentuk sederhana.
    filename   : nama file gambar (contoh: "player.png")
    default_color : warna fallback (R,G,B)
    shape      : "rect", "circle", atau "diamond"
    default_emoji : emoji buat di tengah (opsional)
    """
    try:
        path = os.path.join(IMAGES_DIR, filename)
        img = pygame.image.load(path).convert_alpha()
        # Resize sesuai ukuran cell
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
        
        # Tambah emoji di tengah kalau ada
        if default_emoji:
            font = pygame.font.Font(None, CELL_SIZE // 2)
            emoji_surf = font.render(default_emoji, True, (255, 255, 255))
            emoji_rect = emoji_surf.get_rect(center=(CELL_SIZE//2 - 5, CELL_SIZE//2 - 5))
            img.blit(emoji_surf, emoji_rect)
        
        return img