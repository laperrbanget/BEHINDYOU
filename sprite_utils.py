# sprite_utils.py - Helper load sprite (support subfolder)

import pygame
import os
from settings import IMAGES_DIR, CELL_SIZE

def load_sprite(filename, default_color, shape="rect", default_emoji=None):
    try:
        full_path = os.path.join(IMAGES_DIR, filename)
        img = pygame.image.load(full_path).convert_alpha()
        img = pygame.transform.scale(img, (CELL_SIZE - 10, CELL_SIZE - 10))
        return img
    except:
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
        
        if default_emoji:
            font = pygame.font.Font(None, CELL_SIZE // 2)
            emoji_surf = font.render(default_emoji, True, (255, 255, 255))
            emoji_rect = emoji_surf.get_rect(center=(CELL_SIZE//2 - 5, CELL_SIZE//2 - 5))
            img.blit(emoji_surf, emoji_rect)
        
        return img


def load_wall_texture():
    """Load wall texture - PAKE X DULU (biar kontras!)"""
    # 🔥 LANGSUNG PAKE X TEXTURE
    return create_x_texture()


def create_x_texture():
    """Buat texture dinding pake huruf X kapital - KONTRAST BANGET!"""
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
    
    # Background merah gelap (kontras)
    surf.fill((15, 5, 5))
    
    # Font buat huruf X (besar banget)
    font = pygame.font.Font(None, CELL_SIZE - 4)
    text = font.render("X", True, (255, 255, 255))  
    
    # Posisi di tengah
    text_rect = text.get_rect(center=(CELL_SIZE//2, CELL_SIZE//2 + 2))
    surf.blit(text, text_rect)
    
    # Border tipis
    pygame.draw.rect(surf, (80, 20, 20), (0, 0, CELL_SIZE, CELL_SIZE), 1)
    
    return surf