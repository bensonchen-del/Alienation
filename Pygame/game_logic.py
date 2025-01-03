# game_logic.py
import math
from collections import deque

def bfs(map_layout, start, goal):
    rows, cols = len(map_layout), len(map_layout[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    queue = deque([start])
    visited = set([start])
    parent = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            print(f"BFS path found: {path}")  # Debug 輸出
            return path[::-1]

        for d in directions:
            nx, ny = current[0] + d[0], current[1] + d[1]
            if (0 <= nx < rows and 0 <= ny < cols and 
                (nx, ny) not in visited and map_layout[nx][ny] == " "):
                queue.append((nx, ny))
                visited.add((nx, ny))
                parent[(nx, ny)] = current

    print(f"BFS: No path found from {start} to {goal}")  # Debug 輸出
    return []

def move_towards_target(character, target, dt):
    dx = target[0] - character.rect.centerx
    dy = target[1] - character.rect.centery
    distance = math.hypot(dx, dy)

    if distance < 5:
        return True
    else:
        move_x = (dx / distance) * character.speed * dt
        move_y = (dy / distance) * character.speed * dt
        character.rect.x += move_x
        character.rect.y += move_y
        return False
