import pygame
import math
import os
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1600, 900  # Updated window size
FPS = 60
TILE_SIZE = 40  # Size of each tile in pixels

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Player speeds (pixels per second)
PLAYER_SPEEDS = {'walk': 150, 'run': 300, 'stealth': 75}
ALIEN_SPEED = 200  # pixels per second

# Setup the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Game with Walls")
clock = pygame.time.Clock()

# Load images
def load_image(path, scale=1):
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
player_img = load_image(os.path.join(ASSETS_DIR, 'player.png'), scale=0.25)
player_run_img = load_image(os.path.join(ASSETS_DIR, 'player_r.png'), scale=0.5)
player_stealth_img = load_image(os.path.join(ASSETS_DIR, 'player_s.png'), scale=0.5)
alien_img = load_image(os.path.join(ASSETS_DIR, 'alien.jpg'), scale=0.04)

# Define the map layout (40 columns x 23 rows)
map_layout = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "W                                                          W",
    "W   WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW   W",
    "W   W                                              W        W",
    "W   W   WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW   W",
    "W   W   W                                        W      W  W",
    "W   W   W   WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW      W  W",
    "W   W   W   W                                        W  W",
    "W   W   W   W   WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW    W  W",
    "W   W   W   W   W                             W       W  W",
    "W   W   W   W   W   WWWWWWWWWWWWWWWWWWWWWWWWWWW   W    W  W",
    "W   W   W   W   W   W                         W   W    W  W",
    "W   W   W   W   W   W   WWWWWWWWWWWWWWWWWWWWWWW   W    W  W",
    "W   W   W   W   W   W   W                     W   W    W  W",
    "W   W   W   W   W   W   W   WWWWWWWWWWWWWWWWWWW   W    W  W",
    "W   W   W   W   W   W   W   W                 W   W    W  W",
    "W   W   W   W   W   W   W   W   WWWWWWWWWWWWWWW   W    W  W",
    "W   W   W   W   W   W   W   W   W               W   W    W  W",
    "W   W   W   W   W   W   W   W   W   WWWWWWWWWWWWW   W    W",
    "W   W   W   W   W   W   W   W   W                     W  W",
    "W                                                          W",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
]

# Define Wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLACK)  # Walls are black; you can change the color or use an image
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
        self.state = 'walk'  # Default state
        self.image = self.images[self.state]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_SPEEDS[self.state]

    def update_state(self, new_state):
        if new_state in self.images:
            self.state = new_state
            self.image = self.images[self.state]
            self.speed = PLAYER_SPEEDS[self.state]

    def move(self, dx, dy, walls):
        # Move horizontally
        self.rect.x += dx
        collided_walls = pygame.sprite.spritecollide(self, walls, False)
        if collided_walls:
            if dx > 0:  # Moving right; align to the left side of the wall
                self.rect.right = collided_walls[0].rect.left
            elif dx < 0:  # Moving left; align to the right side of the wall
                self.rect.left = collided_walls[0].rect.right

        # Move vertically
        self.rect.y += dy
        collided_walls = pygame.sprite.spritecollide(self, walls, False)
        if collided_walls:
            if dy > 0:  # Moving down; align to the top side of the wall
                self.rect.bottom = collided_walls[0].rect.top
            elif dy < 0:  # Moving up; align to the bottom side of the wall
                self.rect.top = collided_walls[0].rect.bottom

        # Optional: Keep the player within the screen bounds
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

# Define Alien class
class Alien(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = ALIEN_SPEED  # Constant speed
        self.target = (x, y)      # Initial target is its starting position

    def set_target(self, x, y):
        self.target = (x, y)

    def update_position(self, dt, walls):
        dx = self.target[0] - self.rect.centerx
        dy = self.target[1] - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance != 0:
            # Calculate normalized direction vector
            move_x = (dx / distance) * self.speed * dt
            move_y = (dy / distance) * self.speed * dt

            # Move horizontally
            self.rect.x += move_x
            collided_walls = pygame.sprite.spritecollide(self, walls, False)
            if collided_walls:
                if move_x > 0:  # Moving right
                    self.rect.right = collided_walls[0].rect.left
                elif move_x < 0:  # Moving left
                    self.rect.left = collided_walls[0].rect.right

            # Move vertically
            self.rect.y += move_y
            collided_walls = pygame.sprite.spritecollide(self, walls, False)
            if collided_walls:
                if move_y > 0:  # Moving down
                    self.rect.bottom = collided_walls[0].rect.top
                elif move_y < 0:  # Moving up
                    self.rect.top = collided_walls[0].rect.bottom

# Initialize player and alien
player_start_x, player_start_y = WIDTH // 2, HEIGHT // 2
player = Player(player_img, player_start_x, player_start_y)
alien = Alien(alien_img, 100, 100)

# Create walls
walls = pygame.sprite.Group()

for row_idx, row in enumerate(map_layout):
    for col_idx, tile in enumerate(row):
        if tile == 'W':
            wall_x = col_idx * TILE_SIZE
            wall_y = row_idx * TILE_SIZE
            wall = Wall(wall_x, wall_y, TILE_SIZE, TILE_SIZE)
            walls.add(wall)

# Fonts
pygame.font.init()
font = pygame.font.SysFont(None, 24)

# Key states
keys_pressed = {
    'W': False,
    'A': False,
    'S': False,
    'D': False,
    'Run': False,
    'Stealth': False
}

# Function to draw tiled background
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

    # Update player state based on keys pressed
    if keys_pressed['Stealth']:
        player.update_state('stealth')
    elif keys_pressed['Run']:
        player.update_state('run')
    else:
        player.update_state('walk')

    # Calculate movement deltas
    dx = dy = 0
    if keys_pressed['A']:
        dx -= player.speed * dt
    if keys_pressed['D']:
        dx += player.speed * dt
    if keys_pressed['W']:
        dy -= player.speed * dt
    if keys_pressed['S']:
        dy += player.speed * dt

    # Move the player with collision handling
    player.move(dx, dy, walls)

    # Update alien's target position based on player's current position
    alien.set_target(player.rect.centerx, player.rect.centery)

    # Update alien's position towards the target with collision handling
    alien.update_position(dt, walls)

    # Rendering
    draw_background()                      # Draw the background
    walls.draw(screen)                    # Draw walls
    screen.blit(player.image, player.rect)  # Draw the player
    screen.blit(alien.image, alien.rect)    # Draw the alien

    # Render labels
    player_text = font.render(f'Player X: {player.rect.centerx:.2f}, Y: {player.rect.centery:.2f}', True, WHITE)
    alien_text = font.render(f'Alien Target X: {alien.target[0]:.2f}, Y: {alien.target[1]:.2f}', True, WHITE)
    screen.blit(player_text, (10, HEIGHT - 60))
    screen.blit(alien_text, (10, HEIGHT - 30))

    # Update the display
    pygame.display.flip()

# Clean up
pygame.quit()
