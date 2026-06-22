# level_manager.py
# Mengelola data level, progres pemain, dan konfigurasi tiap level

import json
import os

SAVE_FILE = "save_data.json"

class LevelManager:
    def __init__(self):
        # ========== DATA LEVEL ==========
        # Level 1-5 dengan konfigurasi masing-masing
        self.levels = [
            {
                "id": 1,
                "name": "Pemula",
                "ghost_count": 1,       # Jumlah hantu
                "ghost_teleport_interval": 5000,  # dalam milidetik (5 detik)
                "door_teleport_interval": 8000,   # 8 detik
                "background_color": (20, 50, 30),  # Hijau gelap
                "background_image": "background_lv1.png"
            },
            {
                "id": 2,
                "name": "Menengah",
                "ghost_count": 1,
                "ghost_teleport_interval": 4000,
                "door_teleport_interval": 6000,
                "background_color": (20, 30, 60),  # Biru gelap
                "background_image": "background_lv2.png"
            },
            {
                "id": 3,
                "name": "Sulit",
                "ghost_count": 2,       # MULAI 2 HANTU!
                "ghost_teleport_interval": 3000,
                "door_teleport_interval": 5000,
                "background_color": (60, 30, 20),  # Orange gelap
                "background_image": "background_lv3.png"
            },
            {
                "id": 4,
                "name": "Ekstrem",
                "ghost_count": 2,
                "ghost_teleport_interval": 2500,
                "door_teleport_interval": 4000,
                "background_color": (60, 20, 20),  # Merah gelap
                "background_image": "background_lv4.png"
            },
            {
                "id": 5,
                "name": "Legend",
                "ghost_count": 3,       # 3 HANTU DI LEVEL TERAKHIR!
                "ghost_teleport_interval": 2000,
                "door_teleport_interval": 3000,
                "background_color": (40, 10, 50),  # Ungu gelap
                "background_image": "background_lv5.png"
            }
        ]

        # Progres pemain: level yang sudah di-unlock (mulai dari 1)
        self.unlocked_level = 1
        self.load_progress()

    def load_progress(self):
        """Load save file (kalau ada)"""
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    self.unlocked_level = data.get('unlocked_level', 1)
            except:
                self.unlocked_level = 1
        else:
            self.unlocked_level = 1

    def save_progress(self):
        """Simpan progres ke file"""
        with open(SAVE_FILE, 'w') as f:
            json.dump({'unlocked_level': self.unlocked_level}, f)

    def unlock_next_level(self):
        """Buka level berikutnya (dipanggil saat player menang)"""
        if self.unlocked_level < len(self.levels):
            self.unlocked_level += 1
            self.save_progress()
            return True
        return False  # Sudah di level terakhir

    def get_level_config(self, level_id):
        """Dapatkan konfigurasi level berdasarkan ID (1-5)"""
        for lv in self.levels:
            if lv['id'] == level_id:
                return lv
        return self.levels[0]  # Fallback ke level 1

    def get_total_levels(self):
        return len(self.levels)

    def is_level_unlocked(self, level_id):
        return level_id <= self.unlocked_level