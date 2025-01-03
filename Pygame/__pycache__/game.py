import pygame
import math
import os
import sys
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1600, 1600
FPS = 60
TILE_SIZE = 80

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Player speeds (pixels per second)
PLAYER_SPEEDS = {'walk': 150, 'run': 250, 'stealth': 75}
ALIEN_SPEED = 300  # pixels per second

# Setup the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Game with Walls")
clock = pygame.time.Clock()

# Load images
def load_image(path, scale=1.5):
    try:
        image = pygame.image.load(path).convert_alpha()
        if scale != 1:
            size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Unable to load image at path: {path}")
        raise SystemExit(e)

# Assuming images are in a folder named 'assets' in the same directory
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# Verify assets directory exists
if not os.path.exists(ASSETS_DIR):
    print(f"Assets directory not found at {ASSETS_DIR}")
    sys.exit(1)

background_img = load_image(os.path.join(ASSETS_DIR, 'images.png'), scale=8)
player_img = load_image(os.path.join(ASSETS_DIR, 'player.png'), scale=0.5)
player_run_img = load_image(os.path.join(ASSETS_DIR, 'player_r.png'), scale=0.5)
player_stealth_img = load_image(os.path.join(ASSETS_DIR, 'player_s.png'), scale=0.5)
alien_img = load_image(os.path.join(ASSETS_DIR, 'alien.jpg'), scale=0.05)

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

# Define Wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))

# Define Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.images = {
            'walk': image,
            'run': player_run_img,
            'stealth': player_stealth_img
        }
        self.state = 'walk'
        self.image = self.images[self.state]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_SPEEDS[self.state]

    def update_state(self, new_state):
        if new_state in self.images:
            self.state = new_state
            self.image = self.images[self.state]
            self.speed = PLAYER_SPEEDS[self.state]

    def move(self, dx, dy, walls):
        self.rect.x += dx
        collided_walls = pygame.sprite.spritecollide(self, walls, False)
        if collided_walls:
            if dx > 0:
                self.rect.right = collided_walls[0].rect.left
            elif dx < 0:
                self.rect.left = collided_walls[0].rect.right
        self.rect.y += dy
        collided_walls = pygame.sprite.spritecollide(self, walls, False)
        if collided_walls:
            if dy > 0:
                self.rect.bottom = collided_walls[0].rect.top
            elif dy < 0:
                self.rect.top = collided_walls[0].rect.bottom
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

# Define Alien class
class Alien(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = ALIEN_SPEED
        self.target = (x, y)

    def set_target(self, x, y):
        self.target = (x, y)

    def update_position(self, dt, walls):
        dx = self.target[0] - self.rect.centerx
        dy = self.target[1] - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance != 0:
            move_x = (dx / distance) * self.speed * dt
            move_y = (dy / distance) * self.speed * dt

            # 水平移動
            self.rect.x += move_x
            collided_walls = pygame.sprite.spritecollide(self, walls, False)
            if collided_walls:
                if move_x > 0:  # 向右移動，撞到牆壁的左邊
                    self.rect.right = collided_walls[0].rect.left
                elif move_x < 0:  # 向左移動，撞到牆壁的右邊
                    self.rect.left = collided_walls[0].rect.right

            # 垂直移動
            self.rect.y += move_y
            collided_walls = pygame.sprite.spritecollide(self, walls, False)
            if collided_walls:
                if move_y > 0:  # 向下移動，撞到牆壁的上邊
                    self.rect.bottom = collided_walls[0].rect.top
                elif move_y < 0:  # 向上移動，撞到牆壁的下邊
                    self.rect.top = collided_walls[0].rect.bottom


# Initialize player and alien
player_start_x, player_start_y = WIDTH // 2, HEIGHT // 2
player = Player(player_img, player_start_x, player_start_y)
alien = Alien(alien_img, WIDTH // 2, HEIGHT // 2)

# Create walls
walls = pygame.sprite.Group()
for row_idx, row in enumerate(map_layout):
    for col_idx, tile in enumerate(row):
        if tile == 'W':
            wall_x = col_idx * TILE_SIZE
            wall_y = row_idx * TILE_SIZE
            wall = Wall(wall_x, wall_y, TILE_SIZE, TILE_SIZE)
            walls.add(wall)

# Main loop
running = True
last_update_time = pygame.time.get_ticks()  # 記錄目標最後更新的時間
while running:
    dt = clock.tick(FPS) / 1000  # Delta time in seconds
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update player movement
    dx = dy = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        dy -= player.speed * dt
    if keys[pygame.K_s]:
        dy += player.speed * dt
    if keys[pygame.K_a]:
        dx -= player.speed * dt
    if keys[pygame.K_d]:
        dx += player.speed * dt
    player.move(dx, dy, walls)

    # Update alien target every 3 seconds
    if current_time - last_update_time >= 3000:
        alien.set_target(player.rect.centerx, player.rect.centery)
        last_update_time = current_time

    # Update alien position
    alien.update_position(dt, walls)

    # Rendering
    screen.fill(WHITE)
    walls.draw(screen)
    screen.blit(player.image, player.rect)
    screen.blit(alien.image, alien.rect)

    pygame.display.flip()

pygame.quit()
