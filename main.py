# main.py - Game Utama dengan finish RANDOM!

import pygame
import sys
import random
from settings import *
from map import get_grid
from player import Player
from ghost import Ghost
from search import bfs_path
from sprite_utils import load_sprite
from level_manager import LevelManager
from menu import Menu
from sprite_utils import load_sprite, load_wall_texture
import os

# ========== CLASS GAME (SATU SAJA) ==========
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # ===== UKURAN LAYAR AMAN UNTUK 14 INCH =====
        # Pake ukuran lebih kecil biar muat di layar 14"
        global CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
        
        CELL_SIZE = 35  # Turunin dari 40 ke 35
        SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE   # 15*35 = 525px
        SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + 120  # 15*35 + 120 = 645px
        
        # ===== SET WINDOW FLAGS (BIAR TOMBOL CLOSE KELIHATAN) =====
        # Pake flag RESIZABLE biar tombol minimize/maximize/close muncul
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.RESIZABLE  # <<< PENTING! Biar tombol window keliatan
        )
        pygame.display.set_caption("ESCAPE THE GHOST - Ultimate Edition")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # Level Manager
        self.lm = LevelManager()
        self.current_level = self.lm.unlocked_level
        
        # Load assets
        self.load_assets()
        self.load_sounds()
        
        # Menu
        self.menu = Menu(self.screen, self.lm)
        
        # Game state
        self.in_menu = True
        self.in_level_select = False
        self.reset_game()
    
    def load_assets(self):
        """Load semua gambar (dengan fallback)"""
        # Wall texture
        self.wall_texture = load_wall_texture()
        
        # Heart assets
        self.heart_img = load_sprite("heart.png", RED, "rect")
        self.heart_empty_img = load_sprite("heart_empty.png", GRAY, "rect")
        
        # 🔥 JUMPSCARE: ukuran 70% layar biar besar!
        self.jumpscare_img = load_sprite("ghost_scare.png", RED, "circle")
        if self.jumpscare_img:
            target_width = int(SCREEN_WIDTH * 0.7)   # 70% dari lebar layar
            target_height = int(SCREEN_HEIGHT * 0.7) # 70% dari tinggi layar
            self.jumpscare_img = pygame.transform.smoothscale(self.jumpscare_img, (target_width, target_height))
        
        # Door sprite
        self.door_sprite = load_sprite("door.png", GREEN, "rect", "🚪")
        
        # Background images per level
        self.bg_images = {}
        for i in range(1, 6):
            try:
                img = pygame.image.load(os.path.join(IMAGES_DIR, f"background_lv{i}.png")).convert()
                img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT - 150))
                self.bg_images[i] = img
            except:
                self.bg_images[i] = None
    
    def load_sounds(self):
        """Load sound effects"""
        try:
            self.teleport_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "teleport.mp3"))
            self.hit_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "hit.mp3"))
            self.scare_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "scare.mp3"))
            self.play_level_music()
            self.scream_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "orang_ditusuk.mp3"))
            self.stab_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "knife_stab.mp3"))

        except:
            print("Sound files not found — playing without sound")
            self.teleport_sound = None
            self.hit_sound = None
            self.scare_sound = None
    
    def play_level_music(self):

        music_file = f"bg_music_{self.current_level}.mp3"

        if self.current_level == 1:
            music_file = "bg_music.mp3"

        try:
            pygame.mixer.music.load(
                os.path.join(SOUNDS_DIR, music_file)
            )

            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)

        except Exception as e:
            print(e)

    # ========== LEVEL & MENU METHODS ==========
    
    def start_game(self, level_id):
        """Mulai game di level tertentu"""
        self.current_level = level_id
        self.in_menu = False
        self.in_level_select = False
        self.reset_game()
    
    def show_level_selection(self):
        """Tampilkan layar pilih level"""
        self.in_level_select = True
        self.in_menu = False
        
        # Pilihan level yang tersedia
        self.level_options = []
        for i in range(1, self.lm.get_total_levels() + 1):
            if self.lm.is_level_unlocked(i):
                self.level_options.append(i)
        self.selected_level_index = 0
    
    def draw_level_selection(self):
        """Gambar layar pilih level dengan posisi CENTER (dynamic)"""
        screen_width, screen_height = self.screen.get_width(), self.screen.get_height()
        
        self.screen.fill((15, 15, 30))
            
        title = self.font_big.render("SELECT LEVEL", True, (255, 255, 255))
        title_x = screen_width // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, 80))
            
        # Ukuran tombol level
        btn_width = 300
        btn_height = 50
        
        # Posisi tombol di tengah
        total_height = len(self.level_options) * (btn_height + 15) - 15
        start_y = (screen_height - total_height) // 2 + 50
        
        for i, level_id in enumerate(self.level_options):
            y_pos = start_y + i * (btn_height + 15)
            btn_x = screen_width // 2 - btn_width // 2
            config = self.lm.get_level_config(level_id)
                
            if i == self.selected_level_index:
                # Level yang dipilih (border kuning)
                pygame.draw.rect(self.screen, (255, 255, 100), 
                            (btn_x - 4, y_pos - 4, btn_width + 8, btn_height + 8), 4)
                pygame.draw.rect(self.screen, (60, 60, 120), 
                            (btn_x, y_pos, btn_width, btn_height))
                color = (255, 255, 255)
            else:
                # Level biasa
                unlocked = self.lm.is_level_unlocked(level_id)
                bg_color = (40, 80, 40) if unlocked else (60, 40, 40)
                pygame.draw.rect(self.screen, bg_color, 
                            (btn_x, y_pos, btn_width, btn_height))
                color = (200, 200, 200) if unlocked else (100, 100, 100)
                
            # Text level
            lock_icon = "" if self.lm.is_level_unlocked(level_id) else "🔒 "
            text = self.font_small.render(f"{lock_icon}Level {level_id}: {config['name']}", True, color)
            text_x = screen_width // 2 - text.get_width() // 2
            self.screen.blit(text, (text_x, y_pos + 10))
            
        info = self.font_small.render("UP/DOWN: Navigate | ENTER: Play | ESC: Back", True, (150, 150, 150))
        info_x = screen_width // 2 - info.get_width() // 2
        self.screen.blit(info, (info_x, screen_height - 50))
    
    # ========== GAME METHODS ==========
    
    def reset_game(self, next_level=False):
        """Reset semua state game dengan konfigurasi level"""
        # Kalau next_level=True, naik ke level berikutnya
        if next_level and self.current_level < self.lm.get_total_levels():
            self.current_level += 1
        elif next_level and self.current_level >= self.lm.get_total_levels():
            # Udah di level terakhir, tetep di level terakhir
            pass
        
        self.grid, self.exit_pos = get_grid()
        
        # Dapatkan konfigurasi level
        config = self.lm.get_level_config(self.current_level)
        ghost_count = config['ghost_count']
        self.ghost_teleport_interval = config['ghost_teleport_interval']
        self.door_teleport_interval = config['door_teleport_interval']
        self.bg_color = config['background_color']
        self.play_level_music()
        
        # Cari posisi start yang reachable ke exit
        empty_cells = []
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        
        random.shuffle(empty_cells)
        start_pos = None
        for pos in empty_cells:
            if bfs_path(self.grid, pos, self.exit_pos):
                start_pos = pos
                break
        
        if start_pos:
            self.player = Player(start_pos[0], start_pos[1])
        else:
            self.player = Player(0, 0)
        
        # Spawn GHOSTS (jumlah sesuai level)
        self.ghosts = []
        for _ in range(ghost_count):
            best_pos = None
            max_dist = -1
            for pos in empty_cells:
                if pos != self.player.get_position() and pos != self.exit_pos:
                    dist = abs(pos[0] - self.player.x) + abs(pos[1] - self.player.y)
                    dist_exit = abs(pos[0] - self.exit_pos[0]) + abs(pos[1] - self.exit_pos[1])
                    total_dist = dist + dist_exit
                    if total_dist > max_dist:
                        max_dist = total_dist
                        best_pos = pos
            
            if best_pos:
                self.ghosts.append(Ghost(best_pos[0], best_pos[1]))
            else:
                self.ghosts.append(Ghost(GRID_HEIGHT-2, GRID_WIDTH-2))
        
        # Game state
        self.game_over = False
        self.win = False
        self.auto_path = []
        self.auto_index = 0
        self.flash_alpha = 0
        self.show_path = False
        self.path_points = []
        self.start_time = pygame.time.get_ticks()
        self.last_ghost_teleport = pygame.time.get_ticks()
        self.last_door_teleport = pygame.time.get_ticks()
        
        # Jumpscare state
        self.jumpscare_active = False
        self.jumpscare_timer = 0
    
    def draw_background(self):
        
        if self.current_level in self.bg_images and self.bg_images[self.current_level] is not None:
            self.screen.blit(self.bg_images[self.current_level], (0, 0))
        else:
            self.screen.fill(DARK_GRAY_BG)
    
    def draw_grid(self):
        """Gambar grid dengan WALL TEXTURE PNG dan jalan lebih gelap"""
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                
                if self.grid[row][col] == 1:
                    # DINDING: pake texture PNG
                    self.screen.blit(self.wall_texture, (x, y))
                else:
                    # 🔥 JALAN: lebih gelap (23, 23, 35) dan (33, 33, 45)
                    color = (23, 23, 35) if (row + col) % 2 == 0 else (33, 33, 45)
                    pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, LIGHT_GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)
    
    def draw_path(self):
        """Gambar garis jalur terpendek (Auto-Solve Visualization)"""
        try:
            if not self.show_path:
                return
            
            if not self.path_points or len(self.path_points) < 2:
                return
            
            # Gambar garis
            for i in range(len(self.path_points) - 1):
                start = self.path_points[i]
                end = self.path_points[i+1]
                
                # Cek validasi posisi
                if not start or not end:
                    continue
                
                start_px = start[1] * CELL_SIZE + CELL_SIZE//2
                start_py = start[0] * CELL_SIZE + CELL_SIZE//2
                end_px = end[1] * CELL_SIZE + CELL_SIZE//2
                end_py = end[0] * CELL_SIZE + CELL_SIZE//2
                
                # Garis cyan terang
                pygame.draw.line(self.screen, (0, 255, 255), (start_px, start_py), (end_px, end_py), 4)
            
            # Gambar titik di setiap sel (pakai set biar gak dobel)
            for point in set(self.path_points):
                if point:
                    px = point[1] * CELL_SIZE + CELL_SIZE//2
                    py = point[0] * CELL_SIZE + CELL_SIZE//2
                    pygame.draw.circle(self.screen, (255, 255, 0), (px, py), 5)
        except Exception as e:
            print(f"⚠️ Error di draw_path: {e}")
            # Jangan matikan game, cukup skip gambar
    
    def draw_entities(self):
        """Gambar player (multi-direction), hantu, dan pintu"""
        # Pintu
        exit_x = self.exit_pos[1] * CELL_SIZE
        exit_y = self.exit_pos[0] * CELL_SIZE
        
        glow_surf = pygame.Surface((CELL_SIZE+10, CELL_SIZE+10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 255, 0, 50), (CELL_SIZE//2+5, CELL_SIZE//2+5), CELL_SIZE//2)
        self.screen.blit(glow_surf, (exit_x-5, exit_y-5))
        self.screen.blit(self.door_sprite, (exit_x + 5, exit_y + 5))
        
        # PLAYER (pake sprite multi-direction)
        px = self.player.y * CELL_SIZE
        py = self.player.x * CELL_SIZE
        
        glow = pygame.Surface((CELL_SIZE+10, CELL_SIZE+10), pygame.SRCALPHA)
        pygame.draw.circle(glow, (80, 150, 255, 80), (CELL_SIZE//2+5, CELL_SIZE//2+5), CELL_SIZE//2)
        self.screen.blit(glow, (px-5, py-5))
        
        # Gambar sprite player sesuai arah
        self.screen.blit(self.player.get_sprite(), (px + 5, py + 5))
        
        # GHOSTS
        for ghost in self.ghosts:
            gx = ghost.y * CELL_SIZE
            gy = ghost.x * CELL_SIZE
            
            glow = pygame.Surface((CELL_SIZE+10, CELL_SIZE+10), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 80, 80, 80), (CELL_SIZE//2+5, CELL_SIZE//2+5), CELL_SIZE//2)
            self.screen.blit(glow, (gx-5, gy-5))
            
            self.screen.blit(ghost.get_sprite(), (gx + 5, gy + 5))
    
    def draw_ui(self):
        """Gambar UI: HP (pake asset hati), Timer, Warning"""
        y_offset = GRID_HEIGHT * CELL_SIZE
        
        # HP Bar (pake gambar hati PNG)
        for i in range(3):
            x = 20 + i * 40
            y = y_offset + 15
            if i < self.player.hp:
                self.screen.blit(self.heart_img, (x, y))
            else:
                self.screen.blit(self.heart_empty_img, (x, y))
        
        # Timer
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        timer_text = self.font_small.render(f"⏱️ {elapsed}s", True, WHITE)
        self.screen.blit(timer_text, (SCREEN_WIDTH - 80, y_offset + 20))
        
        # Informasi level
        config = self.lm.get_level_config(self.current_level)
        level_text = self.font_small.render(f"Level {self.current_level}: {config['name']}", True, LIGHT_GRAY)
        self.screen.blit(level_text, (SCREEN_WIDTH//2 - 100, y_offset + 5))
        
        # Peringatan ghost dekat (dari hantu terdekat)
        if self.ghosts:
            min_dist = min(abs(self.player.x - g.x) + abs(self.player.y - g.y) for g in self.ghosts)
            if min_dist <= 3 and not self.game_over and not self.win:
                warning = self.font_small.render("⚠️ GHOST NEAR! ⚠️", True, RED)
                self.screen.blit(warning, (SCREEN_WIDTH//2 - 80, y_offset + 45))
                
                beat = (pygame.time.get_ticks() // 200) % 2
                if beat:
                    warning_big = self.font_big.render("⚠️⚠️⚠️", True, RED)
                    self.screen.blit(warning_big, (SCREEN_WIDTH//2 - 60, y_offset + 15))
        
        # Help text
        if not self.game_over and not self.win:
            help_text = self.font_small.render("←↑↓→: Move | SPACE: Show Path | R: Restart", True, LIGHT_GRAY)
            self.screen.blit(help_text, (10, y_offset + 80))
        
        # Game Over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0,0))
            go_text = self.font_big.render("💀 GAME OVER 💀", True, RED)
            self.screen.blit(go_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2))
            restart_text = self.font_small.render("Press R to Restart Level", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50))
        
        # Win screen
        if self.win:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0,0))
            win_text = self.font_big.render("🎉 YOU ESCAPED! 🎉", True, GREEN)
            self.screen.blit(win_text, (SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2))
            next_text = self.font_small.render("Press R for Next Level", True, WHITE)
            self.screen.blit(next_text, (SCREEN_WIDTH//2 - 90, SCREEN_HEIGHT//2 + 50))
    
    def draw_flash_effect(self):
        if self.flash_alpha > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash.set_alpha(self.flash_alpha)
            flash.fill(RED)
            self.screen.blit(flash, (0,0))
            self.flash_alpha -= 15
    
    def draw_jumpscare(self):
        """Gambar jumpscare (hantu besar) - FULL IMAGE, tanpa teks"""
        if self.jumpscare_active and self.jumpscare_timer > 0:
            if self.jumpscare_img:
                # Gambar di tengah layar
                img_rect = self.jumpscare_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(self.jumpscare_img, img_rect)
            
            self.jumpscare_timer -= 1
            if self.jumpscare_timer <= 0:
                self.jumpscare_active = False
    
    # ========== GAME LOGIC METHODS ==========
    
    def check_collisions(self):
        """Cek tabrakan player dengan SEMUA hantu dan pintu"""
        # Cek tabrakan dengan semua hantu
        for ghost in self.ghosts:
            if self.player.get_position() == ghost.get_position():
                if self.player.take_damage():
                    self.flash_alpha = 120
                    if hasattr(self, 'hit_sound') and self.hit_sound:
                        self.hit_sound.play()
                    # Knockback
                    dx = self.player.x - ghost.x
                    dy = self.player.y - ghost.y
                    if dx != 0:
                        self.player.move(dx, 0, self.grid)
                    if dy != 0:
                        self.player.move(0, dy, self.grid)
                    
                    # Jumpscare kalau HP habis
                    if not self.player.is_alive():
                        self.trigger_jumpscare()
        
        # Cek sampai pintu
        if self.player.get_position() == self.exit_pos:
            self.win = True
            self.handle_win()  # ← PANGGIL FUNGSI INI
    
    def trigger_jumpscare(self):
        """Trigger jumpscare (game over)"""
        pygame.mixer.music.fadeout(500)
        if hasattr(self, 'stab_sound') and self.stab_sound:
            self.stab_sound.play()
        pygame.time.delay(300)
        self.jumpscare_active = True
        # durasi jumpscare 6 detik
        self.jumpscare_timer = 360
        self.game_over = True
        if hasattr(self, 'scream_sound') and self.scream_sound:
            self.scream_sound.play()
    
    def teleport_ghosts(self):
        """Teleport SEMUA hantu ke posisi random"""
        for ghost in self.ghosts:
            empty_cells = []
            for i in range(GRID_HEIGHT):
                for j in range(GRID_WIDTH):
                    if self.grid[i][j] == 0 and (i, j) != self.player.get_position():
                        empty_cells.append((i, j))
            
            if empty_cells:
                new_pos = random.choice(empty_cells)
                ghost.x, ghost.y = new_pos
        self.flash_alpha = 80
        if hasattr(self, 'teleport_sound') and self.teleport_sound:
            self.teleport_sound.play()
    
    def teleport_door(self):
        """Teleport pintu ke posisi random yang reachable"""
        empty_cells = []
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if self.grid[i][j] == 0 and (i, j) != (0, 0):
                    if bfs_path(self.grid, self.player.get_position(), (i, j)):
                        empty_cells.append((i, j))
        
        if empty_cells:
            new_exit = random.choice(empty_cells)
            self.exit_pos = new_exit
            self.flash_alpha = 100
            if hasattr(self, 'teleport_sound') and self.teleport_sound:
                self.teleport_sound.play()
    
    def show_path(self):
        """Tampilkan jalur terpendek (Auto-Solve Visualization)"""
        try:
            start = self.player.get_position()
            goal = self.exit_pos
            
            # Cek apakah start dan goal valid
            if not start or not goal:
                print("Start atau goal tidak valid!")
                self.show_path = False
                self.path_points = []
                return
            
            path = bfs_path(self.grid, start, goal)
            
            if path and len(path) > 1:
                self.path_points = path
                self.show_path = True
                print(f"✅ Path ditemukan! {len(path)} langkah")
            else:
                self.show_path = False
                self.path_points = []
                print("❌ Tidak ada jalur ke pintu!")
        except Exception as e:
            print(f"⚠️ Error di show_path: {e}")
            self.show_path = False
            self.path_points = []
    
    def update_ghosts(self):
        """Update pergerakan SEMUA hantu"""
        for ghost in self.ghosts:
            ghost.move_towards(self.player.x, self.player.y, self.grid)
            
    def restart_level(self):
        """Restart level saat ini (dipanggil pas R ditekan)"""
        # Cek apakah player menang
        if self.win:
            # Kalau menang → lanjut ke level berikutnya
            self.reset_game(next_level=True)
        else:
            # Kalau kalah/ingin restart → reset level yang sama
            self.reset_game(next_level=False)            
            
    def handle_win(self):
        """Handle kemenangan player: unlock level berikutnya"""
        if self.win and not self.game_over:
            # Buka level berikutnya di LevelManager
            if self.current_level == self.lm.unlocked_level:
                self.lm.unlock_next_level()
                print(f"Level {self.current_level} selesai! Level {self.current_level + 1} terbuka!")
    
    # ========== MAIN LOOP ==========
    
    def run(self):
        """Main game loop dengan menu & level selection"""
        running = True
        
        while running:
            # ===== MENU =====
            if self.in_menu:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        sys.exit()
                    action = self.menu.handle_input(event)
                    if action == "Play":
                        self.start_game(self.lm.unlocked_level)
                    elif action == "Select Level":
                        self.show_level_selection()
                    elif action == "Quit":
                        running = False
                        pygame.quit()
                        sys.exit()
                
                self.menu.draw()
                pygame.display.flip()
                self.clock.tick(FPS)
                continue
            
            # ===== LEVEL SELECTION =====
            if self.in_level_select:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        sys.exit()
                    self.handle_level_selection_input(event)
                
                self.draw_level_selection()
                pygame.display.flip()
                self.clock.tick(FPS)
                continue
            
            # ===== GAME LOOP =====
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if not self.game_over and not self.win and not self.jumpscare_active:
                        if event.key == pygame.K_UP:
                            self.player.move(-1, 0, self.grid)
                            self.show_path = False
                        elif event.key == pygame.K_DOWN:
                            self.player.move(1, 0, self.grid)
                            self.show_path = False
                        elif event.key == pygame.K_LEFT:
                            self.player.move(0, -1, self.grid)
                            self.show_path = False
                        elif event.key == pygame.K_RIGHT:
                            self.player.move(0, 1, self.grid)
                            self.show_path = False
                        elif event.key == pygame.K_SPACE:
                            self.show_path()
                    
                    if event.key == pygame.K_r:
                        if self.win:
                            # Kalau menang, lanjut ke level berikutnya
                            self.reset_game(next_level=True)
                        else:
                            # Kalau kalah, restart level yang sama
                            self.reset_game(next_level=False)
            
            # ===== UPDATE =====
            if not self.game_over and not self.win and not self.jumpscare_active:
                now = pygame.time.get_ticks()
                
                if now - self.last_ghost_teleport > self.ghost_teleport_interval:
                    self.teleport_ghosts()
                    self.last_ghost_teleport = now
                
                if now - self.last_door_teleport > self.door_teleport_interval:
                    self.teleport_door()
                    self.last_door_teleport = now
                
                self.update_ghosts()
                self.player.update()
                self.check_collisions()
            
            # ===== DRAW =====
            self.draw_background()
            self.draw_grid()
            self.draw_entities()
            self.draw_path()
            self.draw_ui()
            self.draw_flash_effect()
            self.draw_jumpscare()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()