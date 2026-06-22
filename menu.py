import pygame
import random
import math
from settings import *


# ============================================================
#  UTILS
# ============================================================

CORRUPT_POOL = (
    list("|||///\\\\<<<>>>!!!???###$$$@@@%%%^^^&&&***")
    + [chr(c) for c in range(0x2580, 0x259F)]
    + list("HELPHERE RUNITISNEAR YOUDIE TURNBACK ITSHERE")
)

def corrupt_text(text, intensity):
    return ''.join(
        random.choice(CORRUPT_POOL) if ch != ' ' and random.random() < intensity else ch
        for ch in text
    )

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ============================================================
#  WAJAH JUMPSCARE - dirender pixel demi pixel pakai shapes
# ============================================================

class JumpscareFrame:
    """
    Wajah distorted yang muncul 1-4 frame lalu hilang.
    Tidak pakai gambar eksternal — semua primitive pygame.
    """

    def draw(self, screen, intensity=1.0):
        sw, sh = screen.get_size()
        cx, cy = sw // 2, sh // 2

        # Background putih mati
        flash = pygame.Surface((sw, sh))
        flash.fill((200, 195, 188))
        flash.set_alpha(int(220 * intensity))
        screen.blit(flash, (0, 0))

        # Wajah utama — elips putih pucat
        face_w, face_h = 340, 420
        face_surf = pygame.Surface((face_w + 40, face_h + 40), pygame.SRCALPHA)

        # Kepala
        pygame.draw.ellipse(face_surf, (210, 200, 188, int(255 * intensity)),
                            (20, 20, face_w, face_h))

        # Retakan kulit
        for _ in range(18):
            sx = random.randint(20, face_w)
            sy = random.randint(20, face_h)
            angle = random.uniform(0, math.pi * 2)
            ln = random.randint(10, 50)
            ex = int(sx + ln * math.cos(angle))
            ey = int(sy + ln * math.sin(angle))
            pygame.draw.line(face_surf, (60, 20, 20, 120), (sx, sy), (ex, ey), 1)

        # Mata kiri — rongga hitam dalam
        eye_y = face_h // 3 + 20
        for ex, mirrored in [(face_w // 3, False), (face_w * 2 // 3, True)]:
            # Putih mata bercak
            pygame.draw.ellipse(face_surf, (230, 220, 210, int(255 * intensity)),
                                (ex - 28, eye_y - 14, 56, 30))
            # Rongga hitam
            pygame.draw.ellipse(face_surf, (5, 0, 0, int(255 * intensity)),
                                (ex - 18, eye_y - 9, 36, 20))
            # Iris putih bercahaya (creepy)
            pygame.draw.circle(face_surf, (240, 240, 230, int(200 * intensity)),
                               (ex, eye_y), 6)
            # Pembuluh darah
            for v in range(5):
                va = random.uniform(0, math.pi * 2)
                vlen = random.randint(8, 22)
                pygame.draw.line(face_surf,
                                 (150, 0, 0, random.randint(80, 160)),
                                 (ex, eye_y),
                                 (int(ex + vlen * math.cos(va)),
                                  int(eye_y + vlen * math.sin(va))), 1)
            # Pupil melebar ke atas
            pygame.draw.ellipse(face_surf, (0, 0, 0, int(255 * intensity)),
                                (ex - 4, eye_y - 8, 8, 16))

        # Hidung — lubang gelap dua oval
        nose_y = face_h // 2 + 20
        for nx in [face_w // 2 - 18, face_w // 2 + 8]:
            pygame.draw.ellipse(face_surf, (10, 0, 0, int(200 * intensity)),
                                (nx, nose_y, 20, 14))

        # Mulut — robek horizontal, terlalu lebar
        mouth_y = face_h * 2 // 3 + 20
        mouth_w = face_w // 2 + 40
        mouth_x = face_w // 2 - mouth_w // 2
        pygame.draw.ellipse(face_surf, (5, 0, 0, int(255 * intensity)),
                            (mouth_x + 20, mouth_y, mouth_w - 40, 38))
        # Gigi
        tooth_w = (mouth_w - 40) // 8
        for t in range(8):
            tx = mouth_x + 20 + t * tooth_w
            pygame.draw.rect(face_surf, (200, 195, 185, int(220 * intensity)),
                             (tx + 1, mouth_y + 2, tooth_w - 2, 16))
        # Darah di mulut
        for _ in range(6):
            bx = random.randint(mouth_x + 20, mouth_x + mouth_w - 40)
            pygame.draw.line(face_surf, (120, 0, 0, 180),
                             (bx, mouth_y + 20),
                             (bx + random.randint(-4, 4), mouth_y + 38 + random.randint(0, 10)), 2)

        # Rambut — garis vertikal acak di atas
        for _ in range(30):
            hx = random.randint(20, face_w + 20)
            pygame.draw.line(face_surf, (15, 10, 8, random.randint(80, 180)),
                             (hx, 0), (hx + random.randint(-10, 10), random.randint(60, 140)), 2)

        # Wajah ditengah layar, sedikit miring
        angle_deg = random.uniform(-4, 4)
        rotated = pygame.transform.rotate(face_surf, angle_deg)
        # Scale besar — memenuhi layar
        scale = random.uniform(1.0, 1.4)
        w2 = int(rotated.get_width() * scale)
        h2 = int(rotated.get_height() * scale)
        scaled = pygame.transform.scale(rotated, (w2, h2))
        screen.blit(scaled, (cx - w2 // 2 + random.randint(-30, 30),
                             cy - h2 // 2 + random.randint(-30, 30)))

        # Overlay noise TV saat jumpscare
        noise = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for _ in range(3000):
            nx = random.randint(0, sw - 1)
            ny = random.randint(0, sh - 1)
            v = random.randint(0, 255)
            noise.set_at((nx, ny), (v, 0, 0, random.randint(20, 80)))
        screen.blit(noise, (0, 0))


# ============================================================
#  MATA yang mengikuti kursor (di background)
# ============================================================

class WatchingEye:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size          # radius bola mata
        self.alpha = random.randint(8, 25)
        self.visible = False
        self.cooldown = random.randint(400, 1200)
        self.cooldown_t = random.randint(0, 1000)
        self.duration = random.randint(80, 300)
        self.timer = 0
        self.blink_t = 0
        self.blink_state = 0      # 0=open 1=closing 2=closed 3=opening

    def update(self):
        if self.visible:
            self.timer += 1
            self.blink_t += 1
            # Blink cycle acak
            if self.blink_t > random.randint(120, 400):
                self.blink_state = 1
                self.blink_t = 0
            if self.blink_state == 1:
                pass  # closing (handled in draw)
            if self.timer >= self.duration:
                self.visible = False
                self.cooldown_t = 0
                self.cooldown = random.randint(400, 1200)
        else:
            self.cooldown_t += 1
            if self.cooldown_t >= self.cooldown:
                self.visible = True
                self.timer = 0
                self.blink_t = 0
                self.blink_state = 0

    def draw(self, screen, mouse_x, mouse_y):
        if not self.visible:
            return

        # Fade
        fade = self.timer / max(self.duration, 1)
        a = int(self.alpha * min(fade * 4, (1 - fade) * 4, 1))
        if a <= 0:
            return

        s = self.size
        surf = pygame.Surface((s * 6, s * 4), pygame.SRCALPHA)
        cx, cy = s * 3, s * 2

        # Putih mata (oval)
        pygame.draw.ellipse(surf, (200, 195, 185, a),
                            (0, s // 2, s * 6, s * 3))

        # Arah pupil ke mouse
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
        pupil_travel = s * 0.9
        px = int(cx + dx * pupil_travel)
        py = int(cy + dy * pupil_travel * 0.5)

        # Iris
        pygame.draw.circle(surf, (30, 0, 0, a), (px, py), int(s * 0.9))
        # Pupil
        pygame.draw.circle(surf, (2, 0, 0, a), (px, py), int(s * 0.5))
        # Highlight kecil
        pygame.draw.circle(surf, (220, 210, 200, a // 2),
                           (px - int(s * 0.2), py - int(s * 0.2)), max(1, int(s * 0.2)))

        # Blink — tutup kelopak
        blink_prog = 0
        if self.blink_state == 1:
            blink_prog = min(1.0, (self.blink_t % 20) / 10.0)
        if self.blink_state == 2:
            blink_prog = 1.0
        if blink_prog > 0:
            lid_h = int(s * 1.5 * blink_prog)
            pygame.draw.ellipse(surf, (8, 3, 3, a),
                                (0, s // 2, s * 6, lid_h * 2))
            # Selesai blink
            if blink_prog >= 1.0:
                self.blink_state = 3
            if self.blink_state == 3:
                self.blink_state = 0

        screen.blit(surf, (self.x - cx, self.y - cy))


# ============================================================
#  DINDING BERGERAK (labirin dari tepi)
# ============================================================

class BreathingWall:
    """
    Dinding gelap di tepi yang 'bernafas' — menutup perlahan
    semakin lama player ada di menu (dread escalation).
    """
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.base_inset = 0       # piksel dari tepi, naik seiring waktu

    def update(self, dread_level):
        # Inset meningkat seiring dread, max 120px
        target = dread_level * 120
        self.base_inset = lerp(self.base_inset, target, 0.003)

    def draw(self, screen, tick):
        # Napas sinusoidal
        breath = math.sin(tick / 90.0) * 8
        inset = self.base_inset + breath

        if inset < 1:
            return

        i = int(inset)
        sw, sh = self.sw, self.sh

        # Panel kiri
        lw = max(1, i)
        wall = pygame.Surface((lw, sh), pygame.SRCALPHA)
        for x in range(lw):
            alpha = int(200 * (1 - x / lw) ** 1.5)
            for y in range(sh):
                wall.set_at((x, y), (0, 0, 0, alpha))
        screen.blit(wall, (0, 0))

        # Panel kanan
        wall2 = pygame.Surface((lw, sh), pygame.SRCALPHA)
        for x in range(lw):
            alpha = int(200 * (x / lw) ** 1.5)
            for y in range(sh):
                wall2.set_at((x, y), (0, 0, 0, alpha))
        screen.blit(wall2, (sw - lw, 0))

        # Panel atas (lebih tipis)
        th = max(1, i // 2)
        top = pygame.Surface((sw, th), pygame.SRCALPHA)
        for y in range(th):
            alpha = int(180 * (1 - y / th) ** 2)
            pygame.draw.rect(top, (0, 0, 0, alpha), (0, y, sw, 1))
        screen.blit(top, (0, 0))


# ============================================================
#  SCREEN TEAR (horizontal shift acak, sebentar)
# ============================================================

class ScreenTear:
    def __init__(self):
        self.active = False
        self.tears = []
        self.cooldown = random.randint(180, 600)
        self.cooldown_t = 0
        self.duration = 0
        self.timer = 0

    def update(self):
        if self.active:
            self.timer += 1
            if self.timer >= self.duration:
                self.active = False
                self.tears = []
                self.cooldown = random.randint(180, 600)
                self.cooldown_t = 0
        else:
            self.cooldown_t += 1
            if self.cooldown_t >= self.cooldown:
                self.active = True
                self.timer = 0
                self.duration = random.randint(3, 12)
                sh = 900
                n = random.randint(2, 8)
                self.tears = [
                    (random.randint(0, sh),
                     random.randint(10, sh),
                     random.randint(-60, 60))
                    for _ in range(n)
                ]

    def apply(self, screen):
        if not self.active:
            return
        sw, sh = screen.get_size()
        for y_start, height, shift in self.tears:
            if y_start + height > sh:
                continue
            strip = screen.subsurface((0, y_start, sw, min(height, sh - y_start))).copy()
            screen.fill((4, 2, 2), (0, y_start, sw, min(height, sh - y_start)))
            dest_x = clamp(shift, -(sw // 2), sw // 2)
            screen.blit(strip, (dest_x, y_start))


# ============================================================
#  SUBLIMINAL FRAME — konten disturbing 1-2 frame
# ============================================================

class SubliminalFlash:
    """
    Satu frame teks / pattern disturbing muncul di antara
    frame normal. Hampir tidak terlihat tapi otak merekamnya.
    """
    MESSAGES = [
        "YOU ARE NOT SAFE",
        "DO NOT PRESS ENTER",
        "IT IS STANDING BEHIND YOU",
        "LOOK AWAY",
        "YOU HAVE BEEN FOLLOWED",
        "LEAVE THIS ROOM",
        "I HAVE ALWAYS BEEN HERE",
        "THERE IS NO ESCAPE",
        "DO NOT BLINK",
        "IT KNOWS YOUR NAME",
    ]

    def __init__(self):
        self.cooldown = random.randint(600, 1800)
        self.cooldown_t = 0
        self.active = False
        self.timer = 0
        self.duration = random.randint(1, 3)
        self.msg = ""
        self.font_big = None

    def init_font(self):
        if self.font_big is None:
            self.font_big = pygame.font.Font(None, 80)

    def update(self):
        if self.active:
            self.timer += 1
            if self.timer >= self.duration:
                self.active = False
                self.cooldown = random.randint(600, 1800)
                self.cooldown_t = 0
        else:
            self.cooldown_t += 1
            if self.cooldown_t >= self.cooldown:
                self.active = True
                self.timer = 0
                self.msg = random.choice(self.MESSAGES)

    def draw(self, screen):
        if not self.active:
            return
        self.init_font()
        sw, sh = screen.get_size()
        # Background putih — contrast shock
        flash = pygame.Surface((sw, sh), pygame.SRCALPHA)
        flash.fill((180, 170, 160, 60))
        screen.blit(flash, (0, 0))

        txt = self.font_big.render(self.msg, True, (20, 0, 0))
        x = sw // 2 - txt.get_width() // 2 + random.randint(-20, 20)
        y = sh // 2 - txt.get_height() // 2 + random.randint(-30, 30)
        txt.set_alpha(random.randint(120, 200))
        screen.blit(txt, (x, y))


# ============================================================
#  BAYANGAN CERMIN — bayangan kamu di sisi lain layar
#  (pantulan yang gerakannya tidak sync sempurna)
# ============================================================

class MirrorShadow:
    """
    Siluet hitam di sisi kanan layar — 'pantulan' player
    yang sesekali bergerak sendiri, tidak mengikuti logika.
    """
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.y = screen_h * 0.3
        self.target_y = self.y
        self.phase = 0
        self.visible = False
        self.cooldown = random.randint(500, 1200)
        self.cooldown_t = 0
        self.duration = random.randint(200, 500)
        self.timer = 0
        self.tilt = 0.0
        self.tilt_target = 0.0
        # Sesekali gerak sendiri (glitch)
        self.autonomous_timer = 0
        self.autonomous_active = False

    def update(self, mouse_y):
        if self.visible:
            self.timer += 1
            self.phase += 0.02
            # Sebagian besar waktu ikut mouse, sesekali gerak sendiri
            self.autonomous_timer += 1
            if not self.autonomous_active and self.autonomous_timer > random.randint(180, 400):
                self.autonomous_active = True
                self.autonomous_timer = 0
                self.tilt_target = random.uniform(-0.3, 0.3)
                self.target_y = random.randint(int(self.sh * 0.1), int(self.sh * 0.8))
            if self.autonomous_active and self.autonomous_timer > random.randint(40, 100):
                self.autonomous_active = False
                self.autonomous_timer = 0
                self.tilt_target = 0.0

            if not self.autonomous_active:
                self.target_y = mouse_y

            self.y = lerp(self.y, self.target_y, 0.04)
            self.tilt = lerp(self.tilt, self.tilt_target, 0.05)

            if self.timer >= self.duration:
                self.visible = False
                self.cooldown_t = 0
                self.cooldown = random.randint(500, 1200)
        else:
            self.cooldown_t += 1
            if self.cooldown_t >= self.cooldown:
                self.visible = True
                self.timer = 0

    def draw(self, screen):
        if not self.visible:
            return

        fade = self.timer / max(self.duration, 1)
        base_alpha = int(60 * min(fade * 3, (1 - fade) * 3, 1))
        if base_alpha <= 0:
            return

        # Napas
        breath = math.sin(self.phase) * 8

        # Siluet manusia sederhana (kepala + badan + kaki)
        x = self.sw - 60
        y = int(self.y) + int(breath)
        h = 140   # tinggi total siluet

        surf = pygame.Surface((80, h + 40), pygame.SRCALPHA)
        cx = 40

        # Kepala
        head_r = 18
        pygame.draw.circle(surf, (0, 0, 0, base_alpha),
                           (cx, head_r + 4), head_r)

        # Badan
        badan_top = head_r * 2 + 8
        badan_bot = badan_top + 60
        pygame.draw.polygon(surf, (0, 0, 0, base_alpha), [
            (cx - 20, badan_top),
            (cx + 20, badan_top),
            (cx + 14, badan_bot),
            (cx - 14, badan_bot),
        ])

        # Kaki
        pygame.draw.polygon(surf, (0, 0, 0, base_alpha), [
            (cx - 14, badan_bot),
            (cx - 2, badan_bot),
            (cx - 4, badan_bot + 40),
            (cx - 16, badan_bot + 40),
        ])
        pygame.draw.polygon(surf, (0, 0, 0, base_alpha), [
            (cx + 14, badan_bot),
            (cx + 2, badan_bot),
            (cx + 4, badan_bot + 40),
            (cx + 16, badan_bot + 40),
        ])

        # Tangan — sesekali terangkat sendiri (creepy)
        arm_angle = self.tilt * 3 + math.sin(self.phase * 0.7) * 0.15
        arm_len = 50
        # Tangan kiri
        ax1 = cx - 20
        ay1 = badan_top + 20
        pygame.draw.line(surf, (0, 0, 0, base_alpha),
                         (ax1, ay1),
                         (int(ax1 - arm_len * math.cos(arm_angle)),
                          int(ay1 + arm_len * math.sin(arm_angle + 0.5))), 8)
        # Tangan kanan
        ax2 = cx + 20
        pygame.draw.line(surf, (0, 0, 0, base_alpha),
                         (ax2, ay1),
                         (int(ax2 + arm_len * math.cos(arm_angle)),
                          int(ay1 + arm_len * math.sin(arm_angle + 0.5))), 8)

        # Miring sesuai tilt
        rotated = pygame.transform.rotate(surf, math.degrees(self.tilt) * -1)
        screen.blit(rotated, (x - rotated.get_width() // 2, y - h // 2))

        # Garis tipis seperti "cermin" vertikal
        mirror_alpha = base_alpha // 2
        mirror_surf = pygame.Surface((2, self.sh), pygame.SRCALPHA)
        for py in range(self.sh):
            a = mirror_alpha + int(10 * math.sin(py / 30.0 + self.phase))
            a = clamp(a, 0, 255)
            mirror_surf.set_at((0, py), (30, 0, 0, a))
            mirror_surf.set_at((1, py), (20, 0, 0, a // 2))
        screen.blit(mirror_surf, (self.sw - 80, 0))


# ============================================================
#  RETAKAN + NODA DARAH BACKGROUND
# ============================================================

class BackgroundLayer:
    def __init__(self, screen_w, screen_h):
        # Pre-generate semua ke surface statis — efisien
        self.surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        self._generate(screen_w, screen_h)

    def _generate(self, sw, sh):
        self.surf.fill((0, 0, 0, 0))

        # Noda darah organik
        for _ in range(25):
            cx = random.randint(0, sw)
            cy = random.randint(0, sh)
            n_pts = random.randint(7, 14)
            r_base = random.randint(8, 35)
            pts = []
            for i in range(n_pts):
                a = (i / n_pts) * math.pi * 2
                r = r_base * random.uniform(0.5, 1.3)
                pts.append((int(cx + r * math.cos(a)),
                            int(cy + r * math.sin(a))))
            alpha = random.randint(10, 40)
            color_r = random.randint(40, 80)
            pygame.draw.polygon(self.surf, (color_r, 0, 0, alpha), pts)

        # Retakan
        for _ in range(20):
            self._draw_crack(
                random.randint(0, sw), random.randint(0, sh),
                random.uniform(0, math.pi * 2),
                random.randint(50, 220), random.randint(1, 3), 0
            )

    def _draw_crack(self, x, y, angle, length, width, depth):
        if length < 8 or depth > 3:
            return
        cx, cy = float(x), float(y)
        remaining = length
        while remaining > 6:
            seg = min(random.randint(8, 25), remaining)
            angle += random.uniform(-0.5, 0.5)
            nx = cx + seg * math.cos(angle)
            ny = cy + seg * math.sin(angle)
            c = random.randint(15, 28)
            pygame.draw.line(self.surf, (c, c // 3, c // 3, 80),
                             (int(cx), int(cy)), (int(nx), int(ny)), max(1, width))
            if depth < 3 and random.random() < 0.25:
                self._draw_crack(int(cx), int(cy),
                                 angle + random.uniform(0.5, 1.1) * random.choice([-1, 1]),
                                 seg * 0.5, max(1, width - 1), depth + 1)
            cx, cy = nx, ny
            remaining -= seg

    def draw(self, screen):
        screen.blit(self.surf, (0, 0))


# ============================================================
#  BLOOD DRIP
# ============================================================

class BloodDrip:
    def __init__(self, x, sh):
        self.x = float(x)
        self.sh = sh
        self.y = float(random.randint(-120, -5))
        self.length = random.randint(25, 100)
        self.width = random.randint(2, 6)
        self.speed = random.uniform(0.3, 1.8)
        self.alpha = random.randint(70, 200)
        self.r = random.randint(55, 120)
        self.wobble_freq = random.uniform(0.03, 0.08)
        self.wobble_amp = random.uniform(0.0, 0.8)
        self.phase = random.uniform(0, math.pi * 2)
        self.t = 0

    def update(self):
        self.y += self.speed
        self.x += math.sin(self.phase + self.t * self.wobble_freq) * self.wobble_amp
        self.t += 1
        return self.y < self.sh + 150

    def draw(self, screen):
        surf = pygame.Surface((self.width + 10, self.length + 20), pygame.SRCALPHA)
        cx = (self.width + 10) // 2
        for i in range(self.length):
            a = int(self.alpha * (i / max(self.length, 1)) ** 0.6)
            pygame.draw.rect(surf, (self.r, 0, 0, a),
                             (cx - self.width // 2, i, self.width, 1))
        drop_r = self.width + 2
        pygame.draw.circle(surf, (self.r, 0, 0, self.alpha),
                           (cx, self.length + drop_r), drop_r)
        screen.blit(surf, (int(self.x) - cx, int(self.y) - self.length))


# ============================================================
#  MENU UTAMA
# ============================================================

class Menu:
    def __init__(self, screen, level_manager):
        self.screen = screen
        self.lm = level_manager
        sw, sh = self.get_screen_size()

        # Fonts
        self.font_title  = pygame.font.Font(None, 118)
        self.font_button = pygame.font.Font(None, 52)
        self.font_info   = pygame.font.Font(None, 26)
        self.font_tiny   = pygame.font.Font(None, 20)
        self.font_micro  = pygame.font.Font(None, 16)

        self.selected_option = 0
        self.options = ["Play", "Select Level", "Quit"]
        self.btn_width  = 280
        self.btn_height = 58

        # Sub-systems
        self.bg_layer   = BackgroundLayer(sw, sh)
        self.wall       = BreathingWall(sw, sh)
        self.tear       = ScreenTear()
        self.subliminal = SubliminalFlash()
        self.mirror     = MirrorShadow(sw, sh)
        self.jumpscare  = JumpscareFrame()

        # Mata mengintai (tersebar di background)
        self.eyes = []
        eye_positions = [
            (80, 120, 10), (sw - 90, 80, 12), (sw - 60, sh - 100, 9),
            (50, sh - 80, 11), (sw // 4, sh // 3, 8), (sw * 3 // 4, sh * 2 // 3, 10),
            (sw // 6, sh // 2, 9), (sw * 5 // 6, sh // 4, 11),
            (sw // 3, sh - 60, 8), (sw * 2 // 3, 50, 10),
        ]
        for ex, ey, es in eye_positions:
            self.eyes.append(WatchingEye(ex, ey, es))

        # Drips darah
        self.drips = []
        for _ in range(35):
            d = BloodDrip(random.randint(0, sw), sh)
            d.y = random.uniform(-sh, sh)
            self.drips.append(d)

        # Vignette
        self.vignette = self._build_vignette(sw, sh)

        # State
        self.tick = 0
        self.mouse_x = sw // 2
        self.mouse_y = sh // 2

        # DREAD — naik 0→1 seiring waktu, reset saat player menekan tombol
        self.dread = 0.0
        self.dread_rate = 0.00008   # butuh ~3 menit ke max

        # JUMPSCARE
        self.js_timer    = 0
        self.js_active   = False
        self.js_duration = 0
        self.js_cooldown = random.randint(900, 2400)  # 15–40 detik @ 60fps
        self.js_cooldown_t = 0

        # Title shake
        self.shake_x = 0
        self.shake_y = 0

        # Title glitch
        self.title_display = "BEHIND YOU"
        self.title_glitch_t = 0

        # Pesan tersembunyi (muncul sangat pelan, sangat kecil)
        self.whispers = [
            "look behind you",
            "dont move",
            "its too late",
            "i see you",
            "run",
            "help me",
            "you shouldnt be here",
            "it followed you home",
            "close the game",
            "please leave",
        ]
        self.whisper_alpha = 0.0
        self.whisper_text  = ""
        self.whisper_x     = 0
        self.whisper_y     = 0
        self.whisper_cool  = random.randint(400, 900)
        self.whisper_cool_t = 0

        # Heartbeat — intensitas naik seiring dread
        self.hb_phase = 0.0

        # Wajah di tombol (sangat samar, hampir tidak terlihat)
        self.face_in_button = False
        self.face_btn_t = 0

    # ----------------------------------------------------------
    def get_screen_size(self):
        return self.screen.get_width(), self.screen.get_height()

    def _build_vignette(self, sw, sh):
        v = pygame.Surface((sw, sh), pygame.SRCALPHA)
        max_r = math.hypot(sw / 2, sh / 2)
        for i in range(min(sw // 2, sh // 2)):
            ratio = i / min(sw // 2, sh // 2)
            alpha = int(200 * (1 - ratio) ** 1.6)
            if alpha > 0:
                pygame.draw.rect(v, (0, 0, 0, alpha),
                                 (i, i, sw - 2*i, sh - 2*i), 2)
        return v

    # ----------------------------------------------------------
    def _update_state(self):
        sw, sh = self.get_screen_size()

        self.tick += 1
        self.dread = min(1.0, self.dread + self.dread_rate)

        # Track mouse
        mx, my = pygame.mouse.get_pos()
        self.mouse_x = mx
        self.mouse_y = my

        # Sub-systems
        for eye in self.eyes:
            eye.update()
        self.drips = [d for d in self.drips if d.update()]
        while len(self.drips) < 35:
            self.drips.append(BloodDrip(random.randint(0, sw), sh))
        self.wall.update(self.dread)
        self.tear.update()
        self.subliminal.update()
        self.mirror.update(self.mouse_y)

        # Jumpscare logic
        if not self.js_active:
            self.js_cooldown_t += 1
            if self.js_cooldown_t >= self.js_cooldown:
                self.js_active   = True
                self.js_timer    = 0
                self.js_duration = random.randint(3, 7)
        else:
            self.js_timer += 1
            if self.js_timer >= self.js_duration:
                self.js_active    = False
                self.js_cooldown_t = 0
                self.js_cooldown  = random.randint(900, 2400)

        # Title glitch
        self.title_glitch_t += 1
        if random.random() < 0.006 + self.dread * 0.02:
            self.title_display = corrupt_text("BEHIND YOU", random.uniform(0.15, 0.5))
            self.title_glitch_t = 0
        elif self.title_glitch_t > 8:
            if random.random() < 0.03:
                self.title_display = corrupt_text("BEHIND YOU", 0.05)
            else:
                self.title_display = "BEHIND YOU"

        # Shake saat dread tinggi
        if self.dread > 0.5 and self.tick % 200 < 15:
            intensity = int(4 * self.dread)
            self.shake_x = random.randint(-intensity, intensity)
            self.shake_y = random.randint(-intensity // 2, intensity // 2)
        else:
            self.shake_x = 0
            self.shake_y = 0

        # Whisper messages
        self.whisper_cool_t += 1
        if self.whisper_cool_t >= self.whisper_cool and self.whisper_alpha <= 0:
            self.whisper_text  = random.choice(self.whispers)
            self.whisper_x     = random.randint(sw // 6, sw * 5 // 6)
            self.whisper_y     = random.randint(sh // 5, sh * 4 // 5)
            self.whisper_cool  = random.randint(300, 800)
            self.whisper_cool_t = 0
        if self.whisper_text:
            if self.whisper_alpha < 45:
                self.whisper_alpha += 1.5
            else:
                self.whisper_alpha -= 0.8
                if self.whisper_alpha <= 0:
                    self.whisper_alpha = 0
                    self.whisper_text  = ""

        # Heartbeat
        self.hb_phase += 0.04 + self.dread * 0.06

        # Wajah di tombol
        if random.random() < 0.001 + self.dread * 0.003:
            self.face_in_button = True
            self.face_btn_t = 0
        if self.face_in_button:
            self.face_btn_t += 1
            if self.face_btn_t > 6:
                self.face_in_button = False

    # ----------------------------------------------------------
    def _draw_bg(self):
        self.screen.fill((4, 2, 2))
        self.bg_layer.draw(self.screen)

    def _draw_noise(self, sw, sh):
        """Noise pixel merah berubah tiap beberapa frame"""
        if self.tick % 3 != 0:
            return
        density = int(sw * sh * (0.003 + self.dread * 0.005))
        ns = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for _ in range(density):
            nx = random.randint(0, sw - 1)
            ny = random.randint(0, sh - 1)
            v  = random.randint(15, 60)
            a  = random.randint(8, 30)
            ns.set_at((nx, ny), (v, 0, 0, a))
        self.screen.blit(ns, (0, 0))

    def _draw_scanlines(self, sw, sh):
        scan = pygame.Surface((sw, 1), pygame.SRCALPHA)
        scan.fill((0, 0, 0, 18))
        off = self.tick % 4
        for y in range(off, sh, 6):
            self.screen.blit(scan, (0, y))

    def _draw_heartbeat_vignette(self, sw, sh):
        """Vignette berdenyut seperti detak jantung"""
        pulse = math.sin(self.hb_phase)
        # Double beat pattern
        pulse2 = math.sin(self.hb_phase * 2.2 + 0.5)
        beat = max(0, pulse * 0.6 + pulse2 * 0.4)
        base_alpha = int(30 + beat * 80 * self.dread)
        if base_alpha < 5:
            return
        hb = pygame.Surface((sw, sh), pygame.SRCALPHA)
        hb.fill((0, 0, 0, 0))
        for i in range(min(sw // 2, sh // 2) // 3):
            ratio = i / (min(sw // 2, sh // 2) // 3)
            a = int(base_alpha * (1 - ratio) ** 2)
            if a > 0:
                pygame.draw.rect(hb, (20, 0, 0, a),
                                 (i*3, i*3, sw - 6*i, sh - 6*i), 4)
        self.screen.blit(hb, (0, 0))

    def _draw_title(self, sw, sh):
        ty = 85 + self.shake_y

        # Drop shadow berlapis
        for o in range(9, 0, -1):
            r = o * 11
            sh_surf = self.font_title.render(self.title_display, True, (r, 0, 0))
            self.screen.blit(sh_surf,
                             (sw // 2 - sh_surf.get_width() // 2 + o * 2 + self.shake_x,
                              ty + o * 2))

        # Chromatic aberration (makin parah saat dread tinggi)
        shift = int(2 + self.dread * 6)
        r_surf = self.font_title.render(self.title_display, True, (200, 0, 0))
        b_surf = self.font_title.render(self.title_display, True, (0, 0, 60))
        r_surf.set_alpha(int(40 + self.dread * 60))
        b_surf.set_alpha(int(40 + self.dread * 60))
        base_x = sw // 2 - r_surf.get_width() // 2 + self.shake_x
        self.screen.blit(r_surf, (base_x - shift, ty))
        self.screen.blit(b_surf, (base_x + shift, ty + 1))

        # Title utama
        t_surf = self.font_title.render(self.title_display, True, (165, 18, 18))
        self.screen.blit(t_surf, (sw // 2 - t_surf.get_width() // 2 + self.shake_x, ty))

        # Tetesan dari title
        title_bot = ty + self.font_title.get_height()
        for _ in range(random.randint(0, 3)):
            dx = sw // 2 - t_surf.get_width() // 2 + random.randint(0, t_surf.get_width())
            dl = random.randint(10, 40)
            ds = pygame.Surface((3, dl), pygame.SRCALPHA)
            for j in range(dl):
                a = max(0, 90 - j * 3)
                pygame.draw.rect(ds, (70, 0, 0, a), (0, j, 3, 1))
            self.screen.blit(ds, (dx, title_bot))

        # Subtitle
        sub = self.font_info.render("~~ You can't escape what's behind you ~~", True, (70, 15, 15))
        self.screen.blit(sub, (sw // 2 - sub.get_width() // 2 + self.shake_x, 175))

    def _draw_buttons(self, sw, sh):
        total_h = len(self.options) * (self.btn_height + 22) - 22
        start_y = (sh - total_h) // 2 + 80

        for i, opt in enumerate(self.options):
            y = start_y + i * (self.btn_height + 22)
            bx = sw // 2 - self.btn_width // 2
            is_sel = (i == self.selected_option)

            if is_sel:
                pulse = 0.5 + 0.5 * math.sin(self.tick / 14.0)
                pa = int(20 + 40 * pulse)

                # Wajah sangat samar di dalam tombol (psychological horror)
                if self.face_in_button:
                    for fx in range(bx, bx + self.btn_width, 4):
                        for fy in range(y, y + self.btn_height, 4):
                            dist = math.hypot(fx - (bx + self.btn_width // 2),
                                              fy - (y + self.btn_height // 2))
                            if dist < 20:
                                c = int(12 * (1 - dist / 20))
                                self.screen.set_at((fx, fy), (c + 4, 0, 0))

                # Glow luar berdenyut
                glow = pygame.Surface((self.btn_width + 80, self.btn_height + 80), pygame.SRCALPHA)
                for j in range(6, 0, -1):
                    a = max(0, pa - j * 5)
                    pygame.draw.rect(glow, (210, 0, 0, a),
                                     (j * 7, j * 7,
                                      self.btn_width + 80 - j * 14,
                                      self.btn_height + 80 - j * 14), 3)
                self.screen.blit(glow, (bx - 40, y - 40))

                pygame.draw.rect(self.screen, (50, 7, 7),
                                 (bx, y, self.btn_width, self.btn_height))
                br = int(160 + 80 * pulse)
                pygame.draw.rect(self.screen, (br, 20, 20),
                                 (bx - 2, y - 2, self.btn_width + 4, self.btn_height + 4), 2)

                # Panah kiri
                pygame.draw.polygon(self.screen, (200, 25, 25), [
                    (bx - 16, y + self.btn_height // 2),
                    (bx - 4,  y + self.btn_height // 2 - 8),
                    (bx - 4,  y + self.btn_height // 2 + 8),
                ])

                color = (255, 85, 85)
                label = corrupt_text(opt, 0.12) if random.random() < 0.05 else opt
            else:
                pygame.draw.rect(self.screen, (12, 3, 3),
                                 (bx, y, self.btn_width, self.btn_height))
                pygame.draw.rect(self.screen, (30, 8, 8),
                                 (bx, y, self.btn_width, self.btn_height), 1)
                color = (130, 28, 28)
                label = opt

            txt = self.font_button.render(label, True, color)
            self.screen.blit(txt, (sw // 2 - txt.get_width() // 2,
                                   y + self.btn_height // 2 - txt.get_height() // 2))

    def _draw_whispers(self):
        if not self.whisper_text or self.whisper_alpha <= 0:
            return
        surf = self.font_micro.render(self.whisper_text, True, (80, 15, 15))
        surf.set_alpha(int(self.whisper_alpha))
        self.screen.blit(surf, (self.whisper_x - surf.get_width() // 2,
                                self.whisper_y))

    def _draw_footer(self, sw, sh):
        # Info level — sangat redup
        info = self.font_info.render(
            f"Level Unlocked: {self.lm.unlocked_level}/{self.lm.get_total_levels()}",
            True, (60, 14, 14)
        )
        self.screen.blit(info, (20, sh - 52))

        ctrl = self.font_info.render(
            "[UP/DOWN] Navigate  -  [ENTER] Select",
            True, (45, 10, 10)
        )
        self.screen.blit(ctrl, (sw // 2 - ctrl.get_width() // 2, sh - 28))

    def _draw_blood_floor(self, sw, sh):
        floor_h = 14
        floor = pygame.Surface((sw, floor_h), pygame.SRCALPHA)
        for x in range(sw):
            peak = random.randint(5, floor_h)
            for y in range(peak):
                a = max(0, int(130 * (peak - y) / peak))
                floor.set_at((x, y), (65, 0, 0, a))
        self.screen.blit(floor, (0, sh - floor_h))

    def _draw_dread_indicator(self, sw, sh):
        """Semakin tinggi dread, semakin banyak efek extreme"""
        if self.dread < 0.3:
            return
        # Bercak merah di tepi layar seperti berdarah
        intensity = (self.dread - 0.3) / 0.7
        edge = pygame.Surface((sw, sh), pygame.SRCALPHA)

        # Kiri
        for x in range(int(40 * intensity)):
            a = int(60 * intensity * (1 - x / (40 * intensity + 1)))
            pygame.draw.rect(edge, (60, 0, 0, a), (x, 0, 1, sh))
        # Kanan
        for x in range(int(40 * intensity)):
            a = int(60 * intensity * (1 - x / (40 * intensity + 1)))
            pygame.draw.rect(edge, (60, 0, 0, a), (sw - 1 - x, 0, 1, sh))
        # Bawah
        for y in range(int(50 * intensity)):
            a = int(80 * intensity * (1 - y / (50 * intensity + 1)))
            pygame.draw.rect(edge, (80, 0, 0, a), (0, sh - 1 - y, sw, 1))

        self.screen.blit(edge, (0, 0))

    # ----------------------------------------------------------
    def draw(self):
        sw, sh = self.get_screen_size()
        self._update_state()

        # ---- LAYER DASAR ----
        self._draw_bg()
        self._draw_noise(sw, sh)

        # ---- ENTITIES ----
        for eye in self.eyes:
            eye.draw(self.screen, self.mouse_x, self.mouse_y)
        self.mirror.draw(self.screen)

        for d in self.drips:
            d.draw(self.screen)

        # ---- POST-PROCESS ----
        self.wall.draw(self.screen, self.tick)
        self.screen.blit(self.vignette, (0, 0))
        self._draw_heartbeat_vignette(sw, sh)
        self._draw_dread_indicator(sw, sh)
        self._draw_scanlines(sw, sh)

        # ---- SCREEN TEAR ----
        self.tear.apply(self.screen)

        # ---- UI ----
        self._draw_title(sw, sh)
        self._draw_buttons(sw, sh)
        self._draw_whispers()
        self._draw_footer(sw, sh)
        self._draw_blood_floor(sw, sh)

        # ---- SUBLIMINAL ----
        self.subliminal.draw(self.screen)

        # ---- JUMPSCARE (layer paling atas) ----
        if self.js_active:
            fade = min(1.0, (self.js_duration - self.js_timer) / max(self.js_duration, 1) * 3)
            self.jumpscare.draw(self.screen, intensity=clamp(fade, 0.3, 1.0))

    # ----------------------------------------------------------
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                # Tiap interaksi: brief dread spike lalu sedikit turun
                self.dread = min(1.0, self.dread + 0.05)
                return None
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                self.dread = min(1.0, self.dread + 0.05)
                return None
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_option]
        return None