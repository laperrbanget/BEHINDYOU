# ghost.py - Class Hantu dengan A* + sprite support

import random
import pygame
import heapq
from sprite_utils import load_sprite

class Ghost:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.move_delay = 15  # gerak tiap 15 frame
        self.move_counter = 0
        
        # Load sprite (fallback ke bentuk geometris + emoji)
        self.sprite = load_sprite("ghost.png", (255, 80, 80), "circle", "👻")
    
    def get_sprite(self):
        return self.sprite
    
    def a_star_next_step(self, start, goal, grid):
        """A* buat cari langkah selanjutnya menuju player"""
        rows, cols = len(grid), len(grid[0])
        
        open_set = []
        heapq.heappush(open_set, (0, 0, (start[0], start[1])))
        
        came_from = {}
        g_score = {start: 0}
        f_score = {start: abs(start[0]-goal[0]) + abs(start[1]-goal[1])}
        
        while open_set:
            _, _, current = heapq.heappop(open_set)
            
            if current == goal:
                # Reconstruct path sampe langkah pertama
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                if path:
                    return path[-1]  # langkah pertama
                return start
            
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                nx, ny = current[0] + dx, current[1] + dy
                neighbor = (nx, ny)
                
                if 0 <= nx < rows and 0 <= ny < cols:
                    if grid[nx][ny] == 1:  # dinding
                        continue
                    
                    tentative_g = g_score[current] + 1
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f = tentative_g + abs(nx - goal[0]) + abs(ny - goal[1])
                        f_score[neighbor] = f
                        heapq.heappush(open_set, (f, len(open_set), neighbor))
        
        return start  # fallback
    
    def move_towards(self, target_x, target_y, grid):
        self.move_counter += 1
        if self.move_counter < self.move_delay:
            return (self.x, self.y)
        
        self.move_counter = 0
        
        # Pake A* buat dapet langkah terbaik
        next_pos = self.a_star_next_step((self.x, self.y), (target_x, target_y), grid)
        self.x, self.y = next_pos
        return (self.x, self.y)
    
    def get_position(self):
        return (self.x, self.y)