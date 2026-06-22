# search.py - Algoritma BFS (AMAN)

from collections import deque

def bfs_path(grid, start, goal):
    """Cari jalur terpendek dari start ke goal pake BFS"""
    # Validasi input
    if not grid or not start or not goal:
        return []
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Cek apakah start dan goal di dalam grid
    if not (0 <= start[0] < rows and 0 <= start[1] < cols):
        return []
    if not (0 <= goal[0] < rows and 0 <= goal[1] < cols):
        return []
    
    # Cek apakah start dan goal bukan dinding
    if grid[start[0]][start[1]] == 1:
        return []
    if grid[goal[0]][goal[1]] == 1:
        return []
    
    queue = deque([(start, [start])])
    visited = set([start])
    
    while queue:
        (x, y), path = queue.popleft()
        
        if (x, y) == goal:
            return path
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                if grid[nx][ny] != 1 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
    
    return []