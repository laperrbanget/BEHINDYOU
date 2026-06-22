# player.py - Class Player dengan sprite

import pygame
from sprite_utils import load_sprite

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 3
        self.invincible_timer = 0
        
        # Load sprite
        self.sprite = load_sprite("player.png", (80, 150, 255), "diamond", "🧑")
    
    def get_sprite(self):
        """Return sprite untuk digambar"""
        if self.invincible_timer > 0 and self.invincible_timer % 6 < 3:
            # Efek blink: kasih transparan
            alpha_surf = self.sprite.copy()
            alpha_surf.set_alpha(128)
            return alpha_surf
        return self.sprite
    
    # ... sisanya sama kayak sebelumnya (move, take_damage, update, dll) ...
    def move(self, dx, dy, grid):
        new_x = self.x + dx
        new_y = self.y + dy
        
        if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]):
            if grid[new_x][new_y] != 1:
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