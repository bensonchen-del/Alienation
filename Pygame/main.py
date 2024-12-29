import pygame
import os
import sys
from character import Player, Alien

# Constants
WIDTH, HEIGHT = 1500, 1500
FPS = 60
TILE_SIZE = 80

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Main Game")
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

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
if not os.path.exists(ASSETS_DIR):
    print(f"Assets directory not found at {ASSETS_DIR}")
    sys.exit(1)

background_img = load_image(os.path.join(ASSETS_DIR, 'images.png'), scale=8)
player_img = load_image(os.path.join(ASSETS_DIR, 'player.png'), scale=0.65)
player_run_img = load_image(os.path.join(ASSETS_DIR, 'player_r.png'), scale=0.65)
player_stealth_img = load_image(os.path.join(ASSETS_DIR, 'player_s.png'), scale=0.65)
alien_img = load_image(os.path.join(ASSETS_DIR, 'alien.jpg'), scale=0.07)

# Map layout
map_layout = [
    "WWWWWWWWWWWWWWWWWWW",
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

# Create walls
walls = pygame.sprite.Group()
for row_idx, row in enumerate(map_layout):
    for col_idx, tile in enumerate(row):
        if tile == 'W':
            wall = Wall(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            walls.add(wall)

# Initialize player and alien
player = Player(player_img, player_run_img, player_stealth_img, WIDTH // 2, HEIGHT // 2)
alien = Alien(alien_img, WIDTH // 2, HEIGHT // 2)

# Key states
keys_pressed = {
    'W': False,
    'A': False,
    'S': False,
    'D': False,
    'Run': False,
    'Stealth': False
}

# Function to draw background
def draw_background():
    bg_rect = background_img.get_rect()
    for x in range(0, WIDTH, bg_rect.width):
        for y in range(0, HEIGHT, bg_rect.height):
            screen.blit(background_img, (x, y))

# Main loop
running = True
while running:
    dt = clock.tick(FPS) / 1000  # Delta time in seconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            pressed = event.type == pygame.KEYDOWN
            if event.key == pygame.K_w:
                keys_pressed['W'] = pressed
            elif event.key == pygame.K_a:
                keys_pressed['A'] = pressed
            elif event.key == pygame.K_s:
                keys_pressed['S'] = pressed
            elif event.key == pygame.K_d:
                keys_pressed['D'] = pressed
            elif event.key == pygame.K_SPACE:
                keys_pressed['Run'] = pressed
            elif event.key == pygame.K_c and pressed:
                keys_pressed['Stealth'] = not keys_pressed['Stealth']

    # Update player state
    if keys_pressed['Stealth']:
        player.update_state('stealth')
    elif keys_pressed['Run']:
        player.update_state('run')
    else:
        player.update_state('walk')

    # Player movement
    dx = dy = 0
    if keys_pressed['A']:
        dx -= player.speed * dt
    if keys_pressed['D']:
        dx += player.speed * dt
    if keys_pressed['W']:
        dy -= player.speed * dt
    if keys_pressed['S']:
        dy += player.speed * dt

    player.move(dx, dy, walls)

    # Alien movement
    alien.set_target(player.rect.centerx, player.rect.centery)
    alien.update_position(dt, walls)

    # Rendering
    draw_background()
    walls.draw(screen)
    screen.blit(player.image, player.rect)
    screen.blit(alien.image, alien.rect)

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()

