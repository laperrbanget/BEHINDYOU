# maze_renderer.py - BEHIND YOU | Psychological Horror Maze Renderer
#
# Visual horror berlapis untuk maze:
#   1. WALLS         - tekstur dinding berdarah, retakan, noda organik
#   2. FLOOR         - lantai gelap dengan pola distorted, genangan darah
#   3. CELL PULSE    - sel bernapas, berdenyut seperti jantung
#   4. CORRUPTION    - glitch sel acak, warna salah sebentar
#   5. VEINS         - pembuluh darah menjalar di antara dinding
#   6. FOG           - kabut merah menyelimuti ujung maze
#   7. DRIP          - darah menetes dari dinding ke lantai
#   8. DREAD ESCALATION - semakin lama, semakin parah efeknya

import pygame
import random
import math
from settings import *


# ============================================================
#  UTILS (sama dgn menu.py)
# ============================================================

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ============================================================
#  KONSTANTA WARNA (diambil dari design language menu.py)
# ============================================================

# Background & base
COL_BG          = (4, 2, 2)
COL_WALL_DARK   = (8, 2, 2)
COL_WALL_MID    = (22, 5, 5)
COL_WALL_EDGE   = (38, 8, 8)

# Blood spectrum
COL_BLOOD_DARK  = (40, 0, 0)
COL_BLOOD_MID   = (80, 0, 0)
COL_BLOOD_VIVID = (120, 0, 0)
COL_BLOOD_FRESH = (160, 8, 8)

# Floor
COL_FLOOR_BASE  = (6, 2, 2)
COL_FLOOR_MID   = (14, 4, 4)
COL_FLOOR_LIGHT = (20, 6, 6)

# Accent (pale bone / rotten flesh)
COL_BONE        = (200, 195, 188)
COL_DECAY       = (165, 18, 18)   # sama persis dgn title di menu.py

# Fog
COL_FOG         = (12, 2, 2)


# ============================================================
#  CRACK GENERATOR (di-pre-generate ke surface)
# ============================================================

class CrackSurface:
    """Surface statis berisi retakan + noda — di-generate sekali."""

    def __init__(self, w, h, intensity=1.0):
        self.surf = pygame.Surface((w, h), pygame.SRCALPHA)
        self._generate(w, h, intensity)

    def _draw_crack(self, x, y, angle, length, width, depth):
        if length < 4 or depth > 4:
            return
        cx, cy = float(x), float(y)
        remaining = length
        while remaining > 4:
            seg = min(random.randint(4, 18), remaining)
            angle += random.uniform(-0.6, 0.6)
            nx = cx + seg * math.cos(angle)
            ny = cy + seg * math.sin(angle)
            c = random.randint(10, 25)
            alpha = random.randint(50, 110)
            pygame.draw.line(self.surf, (c, c // 4, c // 4, alpha),
                             (int(cx), int(cy)), (int(nx), int(ny)), max(1, width))
            if depth < 4 and random.random() < 0.28:
                self._draw_crack(int(cx), int(cy),
                                 angle + random.uniform(0.4, 1.0) * random.choice([-1, 1]),
                                 seg * 0.45, max(1, width - 1), depth + 1)
            cx, cy = nx, ny
            remaining -= seg

    def _generate(self, w, h, intensity):
        self.surf.fill((0, 0, 0, 0))

        n_stains = int(8 * intensity)
        for _ in range(n_stains):
            cx = random.randint(0, w)
            cy = random.randint(0, h)
            n_pts = random.randint(5, 12)
            r_base = random.randint(3, int(12 * intensity))
            pts = []
            for i in range(n_pts):
                a = (i / n_pts) * math.pi * 2
                r = r_base * random.uniform(0.4, 1.4)
                pts.append((int(cx + r * math.cos(a)),
                            int(cy + r * math.sin(a))))
            alpha = random.randint(8, 35)
            col_r = random.randint(35, 70)
            pygame.draw.polygon(self.surf, (col_r, 0, 0, alpha), pts)

        n_cracks = int(6 * intensity)
        for _ in range(n_cracks):
            self._draw_crack(
                random.randint(0, w), random.randint(0, h),
                random.uniform(0, math.pi * 2),
                random.randint(20, 60), 1, 0
            )

    def draw(self, screen, x, y):
        screen.blit(self.surf, (x, y))


# ============================================================
#  WALL TILE — satu ubin dinding dengan tekstur horror
# ============================================================

class WallTile:
    """
    Render satu sel dinding dengan:
    - Gradien kedalaman (lebih gelap di tengah)
    - Retakan organik
    - Noda darah
    - Pembuluh darah samar
    """

    _cache = {}   # (w, h) → CrackSurface (shared across tiles)

    def __init__(self, cell_size):
        self.cs = cell_size

    def _get_crack(self, w, h):
        key = (w, h)
        if key not in WallTile._cache:
            WallTile._cache[key] = CrackSurface(w, h, intensity=1.2)
        return WallTile._cache[key]

    def draw(self, screen, px, py, dread=0.0, tick=0, wall_texture=None):
        cs = self.cs

        # ---- Base dinding: gradien sisi ke tengah ----
        if wall_texture:
            # Scale dan tint tekstur sesuai horror palette
            tex = pygame.transform.scale(wall_texture, (cs, cs))
            tint = pygame.Surface((cs, cs), pygame.SRCALPHA)
            # Tint merah gelap di atas tekstur
            tint.fill((8, 0, 0, 140))
            screen.blit(tex, (px, py))
            screen.blit(tint, (px, py))
        else:
            # Fallback: gradien manual
            wall_surf = pygame.Surface((cs, cs))
            wall_surf.fill(COL_WALL_DARK)
            # Edge highlight sangat redup
            pygame.draw.rect(wall_surf, COL_WALL_EDGE, (0, 0, cs, cs), 1)
            screen.blit(wall_surf, (px, py))

        # ---- Inner shadow (kedalaman) ----
        shadow = pygame.Surface((cs, cs), pygame.SRCALPHA)
        # Empat sisi — gradien ke dalam
        for i in range(min(6, cs // 4)):
            a = int(80 * ((6 - i) / 6) ** 2)
            pygame.draw.rect(shadow, (0, 0, 0, a), (i, i, cs - 2*i, cs - 2*i), 1)
        screen.blit(shadow, (px, py))

        # ---- Retakan + noda (dari cache) ----
        crack = self._get_crack(cs, cs)
        crack.draw(screen, px, py)

        # ---- Dread escalation: noda darah makin banyak ----
        if dread > 0.3 and random.random() < 0.0015:
            stain = pygame.Surface((cs, cs), pygame.SRCALPHA)
            cx_s = random.randint(cs // 4, cs * 3 // 4)
            cy_s = random.randint(cs // 4, cs * 3 // 4)
            r_s = random.randint(2, int(5 * dread))
            a_s = int(30 * dread)
            pygame.draw.circle(stain, (60, 0, 0, a_s), (cx_s, cy_s), r_s)
            screen.blit(stain, (px, py))

        # ---- Dread > 0.6: dinding 'bernafas' (bevel bergerak) ----
        if dread > 0.6:
            pulse = math.sin(tick / 70.0 + px * 0.1 + py * 0.07) * 0.5 + 0.5
            bevel_a = int(12 * pulse * (dread - 0.6) / 0.4)
            if bevel_a > 0:
                bevel = pygame.Surface((cs, cs), pygame.SRCALPHA)
                bevel.fill((20, 0, 0, bevel_a))
                screen.blit(bevel, (px, py))


# ============================================================
#  FLOOR TILE — ubin lantai dengan genangan dan pola
# ============================================================

class FloorTile:
    """Lantai gelap dengan:
    - Pola tile samar
    - Genangan darah kering
    - Noda kaki (footprint) hampir tak terlihat
    """

    def draw(self, screen, px, py, cs, dread=0.0, tick=0):
        # ---- Base ----
        floor_surf = pygame.Surface((cs, cs))
        floor_surf.fill(COL_FLOOR_BASE)

        # Pola tile — garis border sangat redup
        border_a = random.randint(4, 10)
        pygame.draw.rect(floor_surf, (border_a, 0, 0), (0, 0, cs, cs), 1)

        # Variasi warna organik antar sel
        noise_col = (
            random.randint(5, 9),
            random.randint(1, 3),
            random.randint(1, 3)
        )
        floor_surf.fill(noise_col)
        pygame.draw.rect(floor_surf, (border_a + 4, 0, 0), (0, 0, cs, cs), 1)

        screen.blit(floor_surf, (px, py))

        # ---- Genangan darah kering (pre-baked per tile, tapi diacak saat draw) ----
        if random.random() < 0.04 + dread * 0.03:
            pool = pygame.Surface((cs, cs), pygame.SRCALPHA)
            pool_w = random.randint(cs // 3, cs * 2 // 3)
            pool_h = random.randint(cs // 6, cs // 3)
            pool_x = random.randint(0, cs - pool_w)
            pool_y = random.randint(0, cs - pool_h)
            pool_a = random.randint(10, 30)
            pygame.draw.ellipse(pool, (40, 0, 0, pool_a),
                                (pool_x, pool_y, pool_w, pool_h))
            screen.blit(pool, (px, py))

        # ---- Dread: lantai mulai 'menggeliat' ----
        if dread > 0.5:
            crawl = math.sin(tick / 55.0 + px * 0.05 + py * 0.08) * 0.5 + 0.5
            crawl_a = int(8 * crawl * (dread - 0.5) / 0.5)
            if crawl_a > 0:
                overlay = pygame.Surface((cs, cs), pygame.SRCALPHA)
                overlay.fill((10, 0, 0, crawl_a))
                screen.blit(overlay, (px, py))


# ============================================================
#  VEIN SYSTEM — pembuluh darah menjalar di antara dinding
# ============================================================

class VeinSystem:
    """
    Pembuluh darah organik yang tumbuh perlahan di atas maze,
    hanya terlihat di sel dinding (walls).
    Intensitas naik seiring dread.
    """

    def __init__(self, grid_w, grid_h, cell_size):
        self.gw = grid_w
        self.gh = grid_h
        self.cs = cell_size
        self.veins = []           # list of {points, alpha, width, pulse_offset}
        self._generate_veins()

    def _generate_veins(self):
        # Pre-generate beberapa jalur vena
        for _ in range(12):
            x = random.uniform(0, self.gw * self.cs)
            y = random.uniform(0, self.gh * self.cs)
            angle = random.uniform(0, math.pi * 2)
            length = random.randint(60, 200)
            pts = []
            cx, cy = x, y
            for _ in range(length // 8):
                angle += random.uniform(-0.4, 0.4)
                step = random.randint(6, 12)
                cx += step * math.cos(angle)
                cy += step * math.sin(angle)
                pts.append((int(cx), int(cy)))
            if len(pts) >= 2:
                self.veins.append({
                    'points': pts,
                    'alpha': random.randint(4, 18),
                    'width': random.randint(1, 2),
                    'pulse_offset': random.uniform(0, math.pi * 2),
                })

    def draw(self, screen, dread, tick):
        if dread < 0.15:
            return
        intensity = (dread - 0.15) / 0.85
        for vein in self.veins:
            pulse = math.sin(tick / 40.0 + vein['pulse_offset']) * 0.5 + 0.5
            a = int(vein['alpha'] * intensity * (0.5 + 0.5 * pulse))
            if a <= 0:
                continue
            col = (int(50 + 30 * pulse), 0, 0)
            pts = vein['points']
            surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            for i in range(len(pts) - 1):
                pygame.draw.line(surf, (*col, a),
                                 pts[i], pts[i + 1], vein['width'])
            screen.blit(surf, (0, 0))


# ============================================================
#  MAZE DRIP — darah menetes dari dinding
# ============================================================

class MazeDrip:
    """Tetesan darah vertikal dari tepi dinding ke lantai."""

    def __init__(self, x, max_y):
        self.x = float(x) + random.uniform(-2, 2)
        self.y = float(random.randint(0, max_y // 3))
        self.max_y = max_y
        self.length = random.randint(6, 30)
        self.width = random.randint(1, 3)
        self.speed = random.uniform(0.15, 0.8)
        self.alpha = random.randint(60, 160)
        self.r = random.randint(50, 110)
        self.phase = random.uniform(0, math.pi * 2)
        self.t = 0
        self.alive = True

    def update(self):
        self.y += self.speed
        self.t += 1
        if self.y > self.max_y + 50:
            self.alive = False

    def draw(self, screen):
        if not self.alive:
            return
        surf = pygame.Surface((self.width + 4, self.length + 10), pygame.SRCALPHA)
        cx = (self.width + 4) // 2
        for i in range(self.length):
            a = int(self.alpha * (i / max(self.length, 1)) ** 0.5)
            pygame.draw.rect(surf, (self.r, 0, 0, a), (cx - self.width // 2, i, self.width, 1))
        drop_r = self.width + 1
        pygame.draw.circle(surf, (self.r, 0, 0, self.alpha), (cx, self.length + drop_r), drop_r)
        screen.blit(surf, (int(self.x) - cx, int(self.y)))


# ============================================================
#  FOG OF DREAD — kabut merah di tepi dan sudut maze
# ============================================================

class DreadFog:
    """
    Kabut atmosferik yang muncul di sudut-sudut dan tepian maze.
    Intensitas naik bersama dread_level.
    """

    def __init__(self, sw, sh):
        self.sw = sw
        self.sh = sh

    def draw(self, screen, dread, tick):
        if dread < 0.1:
            return
        intensity = dread
        fog = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)

        # Sudut kiri atas
        for r in range(int(80 * intensity), 0, -4):
            a = int(18 * intensity * (1 - r / (80 * intensity + 1)) ** 1.5)
            a = clamp(int(a * (0.7 + 0.3 * math.sin(tick / 60.0))), 0, 40)
            if a > 0:
                pygame.draw.circle(fog, (8, 0, 0, a), (0, 0), r)

        # Sudut kanan bawah
        for r in range(int(80 * intensity), 0, -4):
            a = int(15 * intensity * (1 - r / (80 * intensity + 1)) ** 1.5)
            a = clamp(int(a * (0.6 + 0.4 * math.sin(tick / 80.0 + 1.0))), 0, 35)
            if a > 0:
                pygame.draw.circle(fog, (8, 0, 0, a), (self.sw, self.sh), r)

        # Sudut kanan atas
        for r in range(int(60 * intensity), 0, -4):
            a = int(12 * intensity * (1 - r / (60 * intensity + 1)) ** 2)
            a = clamp(int(a * (0.5 + 0.5 * math.sin(tick / 50.0 + 2.0))), 0, 30)
            if a > 0:
                pygame.draw.circle(fog, (6, 0, 0, a), (self.sw, 0), r)

        screen.blit(fog, (0, 0))


# ============================================================
#  CELL CORRUPTION — sel glitch (warna salah sebentar)
# ============================================================

class CellCorruption:
    """
    Sesekali satu sel (floor/wall) berkedip warna yang salah —
    merah vivid, putih tulang, atau hitam total — lalu normal lagi.
    Makin sering seiring dread.
    """

    def __init__(self):
        self.active_cells = {}   # (row, col) → timer
        self.cooldown = random.randint(60, 180)
        self.cooldown_t = 0

    def update(self, grid_h, grid_w, dread):
        self.cooldown_t += 1
        # Spawn corrupt cell baru
        freq = max(20, int(180 - dread * 140))
        if self.cooldown_t >= freq and dread > 0.1:
            r = random.randint(0, grid_h - 1)
            c = random.randint(0, grid_w - 1)
            self.active_cells[(r, c)] = random.randint(2, 8)
            self.cooldown_t = 0

        # Tick existing cells
        to_remove = []
        for key in self.active_cells:
            self.active_cells[key] -= 1
            if self.active_cells[key] <= 0:
                to_remove.append(key)
        for k in to_remove:
            del self.active_cells[k]

    def draw(self, screen, cell_size, dread):
        for (row, col), timer in self.active_cells.items():
            px = col * cell_size
            py = row * cell_size
            # Pilih warna korupsi
            roll = random.random()
            if roll < 0.5:
                col_c = (random.randint(80, 140), 0, 0)   # merah vivid
            elif roll < 0.75:
                col_c = (random.randint(10, 20), random.randint(0, 5), random.randint(0, 5))   # nyaris hitam
            else:
                col_c = (random.randint(160, 200), random.randint(150, 190), random.randint(140, 180))   # tulang
            a = int(160 * dread)
            s = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            s.fill((*col_c, a))
            screen.blit(s, (px, py))


# ============================================================
#  SCANLINE OVERLAY (sama persis seperti menu.py)
# ============================================================

def draw_scanlines(screen, sw, sh, tick, alpha=14):
    scan = pygame.Surface((sw, 1), pygame.SRCALPHA)
    scan.fill((0, 0, 0, alpha))
    off = tick % 4
    for y in range(off, sh, 6):
        screen.blit(scan, (0, y))


# ============================================================
#  CHROMATIC ABERRATION pada sel tertentu
# ============================================================

def draw_chromatic_border(screen, px, py, cs, dread, tick):
    """Outline sel dengan chromatic aberration seperti title di menu.py."""
    if dread < 0.4:
        return
    intensity = (dread - 0.4) / 0.6
    shift = int(1 + intensity * 3)
    a = int(25 * intensity)
    # Merah → geser kiri
    r_s = pygame.Surface((cs, cs), pygame.SRCALPHA)
    pygame.draw.rect(r_s, (200, 0, 0, a), (0, 0, cs, cs), 1)
    screen.blit(r_s, (px - shift, py))
    # Biru → geser kanan
    b_s = pygame.Surface((cs, cs), pygame.SRCALPHA)
    pygame.draw.rect(b_s, (0, 0, 40, a), (0, 0, cs, cs), 1)
    screen.blit(b_s, (px + shift, py))


# ============================================================
#  HEARTBEAT VIGNETTE (sama seperti menu.py, scope maze area)
# ============================================================

def draw_maze_vignette(screen, sw, sh, dread, tick):
    """Vignette berdenyut seperti di menu.py tapi hanya di area maze."""
    hb_phase = tick * (0.04 + dread * 0.06)
    pulse = math.sin(hb_phase)
    pulse2 = math.sin(hb_phase * 2.2 + 0.5)
    beat = max(0, pulse * 0.6 + pulse2 * 0.4)
    base_alpha = int(20 + beat * 60 * dread)
    if base_alpha < 3:
        return
    v = pygame.Surface((sw, sh), pygame.SRCALPHA)
    steps = min(sw // 2, sh // 2) // 4
    for i in range(steps):
        ratio = i / steps
        a = int(base_alpha * (1 - ratio) ** 2)
        if a > 0:
            pygame.draw.rect(v, (15, 0, 0, a),
                             (i * 4, i * 4, sw - 8*i, sh - 8*i), 3)
    screen.blit(v, (0, 0))


# ============================================================
#  MAZE RENDERER — KELAS UTAMA
# ============================================================

class MazeRenderer:
    """
    Renderer maze dengan visual horror yang setara menu.py.

    Dipanggil dari game.py:
        self.maze_renderer = MazeRenderer(screen, grid, wall_texture)
        self.maze_renderer.draw()      # tiap frame
        self.maze_renderer.grid = new_grid   # saat level baru
    """

    def __init__(self, screen, grid, wall_texture=None):
        self.screen       = screen
        self.grid         = grid
        self.wall_texture = wall_texture

        sw = screen.get_width()
        sh = screen.get_height()

        # Ukuran maze sebenarnya (bukan ukuran window) — dipakai utk fog,
        # drips, dan offscreen surface, supaya semua efek konsisten dgn
        # area maze, bukan area window yg bisa lebih besar.
        maze_w, maze_h = self._maze_dims()

        # ---- Sub-systems ----
        self.wall_tile    = WallTile(CELL_SIZE)
        self.floor_tile   = FloorTile()
        self.corruption   = CellCorruption()
        self.fog          = DreadFog(maze_w, maze_h)

        # Vein system — dibuat ulang tiap grid baru
        self._init_veins()

        # Drips — darah menetes dari dinding
        self.drips = []
        self._spawn_initial_drips(maze_w, maze_h)

        # Surface khusus tempat maze digambar, lalu di-blit ke tengah
        # window di akhir draw(). Dibuat ulang otomatis kalau ukuran
        # maze berubah (level baru).
        self._maze_surf   = None
        self._maze_offset = (0, 0)

        # Pre-gen crack surfaces per cell (disampling dari shared cache)
        self.cell_cracks = {}   # (row, col) → CrackSurface

        # Tick (naik tiap frame)
        self.tick = 0

        # DREAD — sama seperti menu.py, naik 0→1 seiring waktu
        self.dread      = 0.0
        self.dread_rate = 0.000055   # sedikit lebih lambat dari menu

        # Noise surface diperbarui tiap N frame
        self._noise_surf = None
        self._noise_tick = -999

        # Screen tear state (sama seperti menu.py)
        self._tear_active  = False
        self._tear_timer   = 0
        self._tear_dur     = 0
        self._tear_cool_t  = 0
        self._tear_cool    = random.randint(300, 900)
        self._tears        = []

    # ----------------------------------------------------------
    def _maze_dims(self):
        """Lebar & tinggi maze dlm pixel, berdasar grid asli (bukan window)."""
        if self.grid:
            gh = len(self.grid)
            gw = len(self.grid[0]) if gh > 0 else GRID_WIDTH
        else:
            gh, gw = GRID_HEIGHT, GRID_WIDTH
        return gw * CELL_SIZE, gh * CELL_SIZE

    def _init_veins(self):
        if self.grid is None:
            self.veins = None
            return
        gh = len(self.grid)
        gw = len(self.grid[0]) if gh > 0 else 0
        self.veins = VeinSystem(gw, gh, CELL_SIZE)

    def _spawn_initial_drips(self, maze_w, maze_h):
        for _ in range(20):
            d = MazeDrip(random.randint(0, maze_w), maze_h)
            d.y = random.uniform(-maze_h, maze_h)
            self.drips.append(d)

    # ----------------------------------------------------------
    def _update(self):
        maze_w, maze_h = self._maze_dims()

        self.tick  += 1
        self.dread  = min(1.0, self.dread + self.dread_rate)

        # Corruption cells
        if self.grid:
            self.corruption.update(len(self.grid), len(self.grid[0]), self.dread)

        # Drips
        self.drips = [d for d in self.drips if (d.update() or d.alive)]
        while len(self.drips) < 18:
            self.drips.append(MazeDrip(random.randint(0, maze_w), maze_h))

        # Screen tear (persis pola menu.py)
        if self._tear_active:
            self._tear_timer += 1
            if self._tear_timer >= self._tear_dur:
                self._tear_active  = False
                self._tears        = []
                self._tear_cool    = random.randint(300, 900)
                self._tear_cool_t  = 0
        else:
            self._tear_cool_t += 1
            if self._tear_cool_t >= self._tear_cool:
                self._tear_active = True
                self._tear_timer  = 0
                self._tear_dur    = random.randint(2, 8)
                sh_px = maze_h
                n = random.randint(1, 5)
                self._tears = [
                    (random.randint(0, sh_px),
                     random.randint(6, sh_px // 3),
                     random.randint(-40, 40))
                    for _ in range(n)
                ]

    # ----------------------------------------------------------
    def _draw_noise(self, sw, sh):
        """Noise pixel merah — update tiap 3 frame, sama seperti menu.py."""
        if self.tick % 3 != 0:
            if self._noise_surf:
                self.screen.blit(self._noise_surf, (0, 0))
            return
        density = int(sw * sh * (0.002 + self.dread * 0.004))
        ns = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for _ in range(density):
            nx = random.randint(0, sw - 1)
            ny = random.randint(0, sh - 1)
            v  = random.randint(10, 50)
            a  = random.randint(5, 22)
            ns.set_at((nx, ny), (v, 0, 0, a))
        self._noise_surf = ns
        self.screen.blit(ns, (0, 0))

    def _apply_tear(self):
        """Screen tear horizontal — sama persis menu.py."""
        if not self._tear_active:
            return
        sw = self.screen.get_width()
        sh_total = self.screen.get_height()
        for y_start, height, shift in self._tears:
            if y_start + height > sh_total or y_start < 0:
                continue
            h = min(height, sh_total - y_start)
            if h <= 0:
                continue
            strip = self.screen.subsurface((0, y_start, sw, h)).copy()
            self.screen.fill((4, 2, 2), (0, y_start, sw, h))
            dest_x = clamp(shift, -(sw // 2), sw // 2)
            self.screen.blit(strip, (dest_x, y_start))

    # ----------------------------------------------------------
    def draw(self):
        """Panggil tiap frame dari game loop."""
        if self.grid is None:
            return

        self._update()

        sw  = self.screen.get_width()
        sh  = self.screen.get_height()
        cs  = CELL_SIZE
        gh  = len(self.grid)
        gw  = len(self.grid[0])

        # ============================================================
        #  LAYER 1 — TILES (wall & floor)
        # ============================================================
        for row in range(gh):
            for col in range(gw):
                px = col * cs
                py = row * cs

                if self.grid[row][col] == 1:
                    # WALL
                    self.wall_tile.draw(
                        self.screen, px, py,
                        dread=self.dread,
                        tick=self.tick,
                        wall_texture=self.wall_texture
                    )
                    # Chromatic border pada dread tinggi
                    draw_chromatic_border(self.screen, px, py, cs, self.dread, self.tick)

                else:
                    # FLOOR
                    self.floor_tile.draw(
                        self.screen, px, py, cs,
                        dread=self.dread,
                        tick=self.tick
                    )

        # ============================================================
        #  LAYER 2 — VEINS (pembuluh darah di atas tiles)
        # ============================================================
        if self.veins:
            self.veins.draw(self.screen, self.dread, self.tick)

        # ============================================================
        #  LAYER 3 — CELL CORRUPTION GLITCH
        # ============================================================
        self.corruption.draw(self.screen, cs, self.dread)

        # ============================================================
        #  LAYER 4 — BLOOD DRIPS
        # ============================================================
        for drip in self.drips:
            drip.draw(self.screen)

        # ============================================================
        #  LAYER 5 — FOG OF DREAD
        # ============================================================
        self.fog.draw(self.screen, self.dread, self.tick)

        # ============================================================
        #  LAYER 6 — RED NOISE (sama dengan menu.py)
        # ============================================================
        self._draw_noise(sw, sh)

        # ============================================================
        #  LAYER 7 — SCANLINES (persis sama seperti menu.py)
        # ============================================================
        draw_scanlines(self.screen, sw, sh, self.tick)

        # ============================================================
        #  LAYER 8 — HEARTBEAT VIGNETTE MAZE
        # ============================================================
        draw_maze_vignette(self.screen, sw, sh, self.dread, self.tick)

        # ============================================================
        #  LAYER 9 — SCREEN TEAR (persis menu.py)
        # ============================================================
        self._apply_tear()

        # ============================================================
        #  LAYER 10 — WALL GRID LINES (tipis, hampir invisible)
        # ============================================================
        # Grid line sangat redup — hanya sebagai panduan sel
        if self.dread < 0.8:
            line_a = int(8 * (1 - self.dread))
            line_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for row in range(gh + 1):
                pygame.draw.line(line_surf, (20, 0, 0, line_a),
                                 (0, row * cs), (gw * cs, row * cs))
            for col in range(gw + 1):
                pygame.draw.line(line_surf, (20, 0, 0, line_a),
                                 (col * cs, 0), (col * cs, gh * cs))
            self.screen.blit(line_surf, (0, 0))

    # ----------------------------------------------------------
    def reset_dread(self, amount=0.05):
        """Panggil saat player menekan tombol (sama seperti menu.py)."""
        self.dread = min(1.0, self.dread + amount)

    def new_level(self, new_grid):
        """Panggil saat level baru dimulai — reset dread, regenerate veins."""
        self.grid  = new_grid
        self.dread = 0.0
        self.cell_cracks.clear()
        WallTile._cache.clear()
        self._init_veins()
        sw = self.screen.get_width()
        maze_h = GRID_HEIGHT * CELL_SIZE
        self.drips = []
        self._spawn_initial_drips(sw, maze_h)