import pygame
import math
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1600, 1600
TILE_SIZE = 80
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Map Layout
map_layout = [
    "WWWWWWWWWWWWWWWWWWWW",
    "W   W       W     W",
    "W W W WWWWW W W W W",
    "W W   W   W W W W W",
    "W WWWWW W WWW W W W",
    "W       W     W   W",
    "W WWWWWWWWWWWWWWW W",
    "W W             W W",
    "W W WWWWWWWWWWW W W",
    "W W W         W W W",
    "W W W WWWWWWW W W W",
    "W W W       W W   W",
    "W W WWWWWWW W WWW W",
    "W W         W     W",
    "W WWWWWWWWWWWWWWWWW",
    "W                 W",
    "WWWWWWWWWWWWWWWWWWW"
]

# Classes for Walls and Characters
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

# BFS for shortest path
def bfs(map_layout, start, goal):
    rows, cols = len(map_layout), len(map_layout[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 上下左右
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
            return path[::-1]  # 返回從起點到終點的路徑

        for d in directions:
            nx, ny = current[0] + d[0], current[1] + d[1]
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited and map_layout[nx][ny] == " ":
                queue.append((nx, ny))
                visited.add((nx, ny))
                parent[(nx, ny)] = current

    return []  # 如果無法到達目標，返回空路徑

# Move towards target
def move_towards_target(character, target, dt):
    dx = target[0] - character.rect.centerx
    dy = target[1] - character.rect.centery
    distance = math.hypot(dx, dy)

    if distance < 5:
        return True  # Reached target
    else:
        character.rect.x += (dx / distance) * character.speed * dt
        character.rect.y += (dy / distance) * character.speed * dt
        return False  # Still moving

# Create wall sprites
walls = pygame.sprite.Group()
for row_idx, row in enumerate(map_layout):
    for col_idx, tile in enumerate(row):
        if tile == 'W':
            walls.add(Wall(col_idx * TILE_SIZE, row_idx * TILE_SIZE))

# Initialize Player and Tracker
player = Character(TILE_SIZE + TILE_SIZE // 2, TILE_SIZE + TILE_SIZE // 2, RED, speed=150)  # Player (Red Ball)
tracker = Character(TILE_SIZE * 10 + TILE_SIZE // 2, TILE_SIZE * 10 + TILE_SIZE // 2, BLUE, speed=300)  # Tracker (Blue Ball)

# Main loop
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Optimized BFS Pathfinding Tracker")
clock = pygame.time.Clock()
running = True
path = []
path_index = 0
goal = (player.rect.centery // TILE_SIZE, player.rect.centerx // TILE_SIZE)

while running:
    dt = clock.tick(FPS) / 1000  # Delta time in seconds

    # Event handling
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_w]:  # Move up
        dy = -1
    if keys[pygame.K_s]:  # Move down
        dy = 1
    if keys[pygame.K_a]:  # Move left
        dx = -1
    if keys[pygame.K_d]:  # Move right
        dx = 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move player
    player.rect.x += dx * player.speed * dt
    player.rect.y += dy * player.speed * dt

    # Recompute path if player has moved
    new_goal = (player.rect.centery // TILE_SIZE, player.rect.centerx // TILE_SIZE)
    if goal != new_goal:
        start = (tracker.rect.centery // TILE_SIZE, tracker.rect.centerx // TILE_SIZE)
        path = bfs(map_layout, start, new_goal)
        path_index = 0
        goal = new_goal

    # Move tracker along the path
    if path_index < len(path):
        target = path[path_index]
        target_pos = (target[1] * TILE_SIZE + TILE_SIZE // 2, target[0] * TILE_SIZE + TILE_SIZE // 2)
        if move_towards_target(tracker, target_pos, dt):
            path_index += 1

    # Draw everything
    screen.fill(WHITE)
    walls.draw(screen)
    screen.blit(player.image, player.rect)
    screen.blit(tracker.image, tracker.rect)

    pygame.display.flip()

pygame.quit()
