# map.py — Chaotic maps 15x15, 100% solveable, no softlock
#
# Semua map di-generate secara algoritmik (random seed + BFS connectivity fix)
# Dijamin: setiap sel kosong reachable dari (0,0)
# Dinding: 22–34% dari total sel — cukup chaos, cukup napas
#
# Cara pakai:
#   from map import get_grid
#   maze, exit_pos = get_grid()
#   # maze[r][c] == 0 → jalan, 1 → dinding
#   # exit_pos = (row, col), dijamin reachable

import random
from collections import deque

# ─────────────────────────────────────────────
#  8 MAP PRE-GENERATED  (seed berbeda, chaos berbeda)
# ─────────────────────────────────────────────

# MAP_1 — seed=42  │ 70 walls (31%)  │ chaotic medium
MAP_1 = [
    [0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1],
    [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
    [1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    [1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    [0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0],
    [0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
]

# MAP_2 — seed=99  │ 58 walls (26%)  │ open but tricky
MAP_2 = [
    [0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
    [1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1],
    [1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1],
]

# MAP_3 — seed=7   │ 75 walls (33%)  │ dense chaos
MAP_3 = [
    [0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0],
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0],
    [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0],
]

# MAP_4 — seed=13  │ 76 walls (34%)  │ hardest
MAP_4 = [
    [0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0],
    [1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0],
    [1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],
    [1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0],
]

# MAP_5 — seed=500 │ 50 walls (22%)  │ open, sneaky traps
MAP_5 = [
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
    [1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
]

# MAP_6 — seed=777 │ 61 walls (27%)  │ scattered clusters
MAP_6 = [
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1],
    [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0],
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
]

# MAP_7 — seed=1337 │ 62 walls (28%)  │ funnel traps
MAP_7 = [
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0],
    [1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1],
    [0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1],
    [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
]

# MAP_8 — seed=2024 │ 64 walls (28%)  │ cluster bombs
MAP_8 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0],
    [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1],
    [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0],
    [1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

ALL_MAPS = [MAP_1, MAP_2, MAP_3, MAP_4, MAP_5, MAP_6, MAP_7, MAP_8]

# ─────────────────────────────────────────────
#  GENERATOR — buat map baru secara algoritmik
#  (opsional, pakai kalau mau variasi tak terbatas)
# ─────────────────────────────────────────────

def generate_chaotic_map(rows=15, cols=15, wall_ratio=0.30, seed=None):
    """
    Generate peta chaos yang fully connected.
    wall_ratio: 0.25–0.35 = sweet spot (chaos tapi playable)
    """
    if seed is not None:
        random.seed(seed)

    maze = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if (r, c) == (0, 0):
                continue
            if random.random() < wall_ratio:
                maze[r][c] = 1

    # BFS connectivity fix — hapus dinding pemisah minimum
    changed = True
    while changed:
        changed = False
        empty = {(r, c) for r in range(rows) for c in range(cols) if maze[r][c] == 0}

        visited = set()
        q = deque([(0, 0)])
        visited.add((0, 0))
        while q:
            r, c = q.popleft()
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if (nr, nc) in empty and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append((nr, nc))

        isolated = empty - visited
        if not isolated:
            break

        for ir, ic in isolated:
            found = False
            bq = deque([(ir, ic)])
            seen = {(ir, ic)}
            while bq and not found:
                r, c = bq.popleft()
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r+dr, c+dc
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        continue
                    if (nr, nc) in seen:
                        continue
                    seen.add((nr, nc))
                    if maze[nr][nc] == 1:
                        for dr2, dc2 in [(-1,0),(1,0),(0,-1),(0,1)]:
                            nr2, nc2 = nr+dr2, nc+dc2
                            if (nr2, nc2) in visited:
                                maze[nr][nc] = 0
                                changed = True
                                found = True
                                break
                        if found:
                            break
                        bq.append((nr, nc))
                    elif (nr, nc) in empty and (nr, nc) not in visited:
                        bq.append((nr, nc))
            if found:
                break

    return maze


# ─────────────────────────────────────────────
#  EXIT PLACEMENT — jauh + reachable via BFS
# ─────────────────────────────────────────────

def get_random_exit(maze):
    """
    Pilih posisi finish yang:
    - Bukan (0,0)
    - Reachable dari (0,0) via BFS
    - Diprioritaskan yang jauh (Manhattan distance tinggi)
    """
    rows, cols = len(maze), len(maze[0])

    # BFS dari (0,0) untuk dapat semua reachable cells + jaraknya
    dist = {}
    q = deque([(0, 0, 0)])
    dist[(0, 0)] = 0
    while q:
        r, c, d = q.popleft()
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if maze[nr][nc] == 0 and (nr, nc) not in dist:
                    dist[(nr, nc)] = d + 1
                    q.append((nr, nc, d + 1))

    # Buang start, urutkan dari yang terjauh
    candidates = sorted(
        [(pos, d) for pos, d in dist.items() if pos != (0, 0)],
        key=lambda x: -x[1]
    )

    # Pilih random dari 25% terjauh supaya tetap menantang
    top_n = max(1, len(candidates) // 4)
    top_candidates = [pos for pos, _ in candidates[:top_n]]

    return random.choice(top_candidates)


# ─────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────

def get_grid(use_generator=False, wall_ratio=0.30):
    """
    Return (maze, exit_pos)

    maze      : list[list[int]], 15×15, 0=jalan 1=dinding
    exit_pos  : (row, col), dijamin reachable dari (0,0)

    use_generator : True  → map baru random setiap kali
                    False → pilih dari 8 pre-built maps (default)
    wall_ratio    : hanya dipakai kalau use_generator=True (0.25–0.35)
    """
    if use_generator:
        maze = generate_chaotic_map(wall_ratio=wall_ratio)
    else:
        maze = [row[:] for row in random.choice(ALL_MAPS)]  # copy supaya aman

    exit_pos = get_random_exit(maze)
    return maze, exit_pos
