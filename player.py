# player.py - Class Player dengan multi-direction sprite

import pygame
from sprite_utils import load_sprite
from settings import CELL_SIZE

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 3
        self.invincible_timer = 0
        self.direction = "down"  # default arah bawah
        
        # Load sprite untuk 4 arah
        self.sprites = {
            "down": load_sprite("player/player_down.png", (80, 150, 255), "diamond", "🧑"),
            "up": load_sprite("player/player_up.png", (80, 150, 255), "diamond", "🧑"),
            "left": load_sprite("player/player_left.png", (80, 150, 255), "diamond", "🧑"),
            "right": load_sprite("player/player_right.png", (80, 150, 255), "diamond", "🧑"),
        }
        
        # Sprite saat ini
        self.sprite = self.sprites["down"]
    
    def get_sprite(self):
        """Return sprite sesuai arah terakhir (dengan efek blink)"""
        # Pilih sprite berdasarkan direction
        self.sprite = self.sprites.get(self.direction, self.sprites["down"])
        
        if self.invincible_timer > 0 and self.invincible_timer % 6 < 3:
            # Efek blink: transparan
            alpha_surf = self.sprite.copy()
            alpha_surf.set_alpha(128)
            return alpha_surf
        return self.sprite
    
    def move(self, dx, dy, grid):
        """Gerak player dan update arah"""
        new_x = self.x + dx
        new_y = self.y + dy
        
        if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]):
            if grid[new_x][new_y] != 1:
                # Update arah berdasarkan gerakan
                if dx < 0:
                    self.direction = "up"
                elif dx > 0:
                    self.direction = "down"
                elif dy < 0:
                    self.direction = "left"
                elif dy > 0:
                    self.direction = "right"
                
                self.x = new_x
                self.y = new_y
                return True
        return False
    
    def take_damage(self):
        if self.invincible_timer <= 0 and self.hp > 0:
            self.hp -= 1
            self.invincible_timer = 30
            return True
        return False
    
    def update(self):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
    
    def get_position(self):
        return (self.x, self.y)
    
    def is_alive(self):
        return self.hp > 0