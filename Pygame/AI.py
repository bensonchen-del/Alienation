import pygame
import math
import random
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1600, 1600
TILE_SIZE = 80
FPS = 60
DISTANCE_THRESHOLD = 300  # Distance in pixels to switch states
WANDER_INTERVAL = 10      # Time in seconds between target changes during wandering
WAITING_DURATION = 5      # Time in seconds to wait in 'waiting' state

# Speed settings
WANDER_SPEED = 150  # Slower speed for wandering
FOLLOW_SPEED = 300  # Faster speed for following

# Visibility settings
VISIBILITY_RADIUS = 200  # Radius of the visibility circle in pixels

# Minimum distance between consecutive wander targets to prevent jitter
MIN_TARGET_DISTANCE = 50  # Reduced from 100 to 50 pixels

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)    # Wander state
GREEN = (0, 255, 0)    # Follow state
YELLOW = (255, 255, 0) # Waiting state
RED = (255, 0, 0)      # Player

# Map Layout (Simplified for Testing)
map_layout = [
    "WWWWWWWWWWWWWWWWWWWW",  # row 0
    "W   W     W     W  W",  # row 1
    "W W W WWW W WWW W WW",  # row 2
    "W W W   W W   W W  W",   # row 3
    "W WWWWW W WWWWW   WW",  # row 4
    "W       W       W  W",  # row 5
    "WWWWWWW W WWWWWWWWWW",  # row 6
    "W             W    W",
    "W             W    W",  # row 7
    "W WWWWWWWWWWW W W  W",   # row 8
    "W W             W  W",   # row 9
    "W W WWWWWWWWW W W  W",   # row 10
    "W W W       W W W  W",   # row 11
    "W W W WWWWW W W W  W",   # row 12
    "W W W     W W   W  W",   # row 13
    "W W WWWWW W WWWWW  W",    # row 14
    "W W       W     W  W",    # row 15
    "W WWWW  WWWWWWWWW  W",    # row 16
    "W                  W",    # row 17
    "WWWWWWWWWWWWWWWWWWWW"
]

# Classes for Walls and Characters
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

class Tracker(pygame.sprite.Sprite):
    def __init__(self, x, y, color, wander_speed, follow_speed, visibility_radius):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2))
        self.color = color
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(x, y))
        self.wander_speed = wander_speed
        self.follow_speed = follow_speed
        self.visibility_radius = visibility_radius

        self.state = 'wander'  # Possible states: 'wander', 'follow', 'waiting'
        self.current_target = None
        self.path = []
        self.path_index = 0
        self.wander_timer = 0
        self.waiting_timer = 0

        self.previous_target_tile = None  # To prevent backtracking

        # Initialize speed based on the starting state
        self.speed = self.wander_speed

    def update(self, dt, player_pos, map_layout, walkable_tiles):
        # State management
        if self.state == 'wander':
            self.wander_timer += dt
            if self.current_target is None:
                self.initialize_tracker_target('wander', map_layout, walkable_tiles)
            else:
                self.move_along_path(dt)
            
            if self.wander_timer >= WANDER_INTERVAL:
                print(f"Wander: {WANDER_INTERVAL} seconds elapsed, selecting new target.")
                self.initialize_tracker_target('wander', map_layout, walkable_tiles)
        
        elif self.state == 'follow':
            self.move_along_path(dt)
        
        elif self.state == 'waiting':
            self.waiting_timer += dt
            if self.waiting_timer >= WAITING_DURATION:
                print("Waiting: Switching back to 'wander' state.")
                self.state = 'wander'
                self.speed = self.wander_speed
                self.update_color(BLUE)
                self.waiting_timer = 0
                self.initialize_tracker_target('wander', map_layout, walkable_tiles)

    def initialize_tracker_target(self, state, map_layout, walkable_tiles):
        if state == 'wander':
            print("\nTracker State: Wander")
            self.update_color(BLUE)
            attempts = 0
            max_attempts = 100
            while attempts < max_attempts:
                tile = random.choice(walkable_tiles)
                target_tile = (tile[0], tile[1])
                current_tile = (self.rect.centery // TILE_SIZE, self.rect.centerx // TILE_SIZE)
                if target_tile != current_tile and target_tile != self.previous_target_tile:
                    candidate_path = bfs(map_layout, current_tile, target_tile)
                    if candidate_path and len(candidate_path) > 1:
                        target_pos = get_tile_position(candidate_path[-1][0],
                                                       candidate_path[-1][1])  # The *final* destination
                        distance = math.hypot(target_pos[0] - self.rect.centerx,
                                              target_pos[1] - self.rect.centery)
                        if distance >= MIN_TARGET_DISTANCE:
                            # Store the full path, start from the first step
                            self.path = candidate_path
                            self.path_index = 1
                            # Our immediate target is the second tile in path 
                            # (because path[0] is our current tile)
                            self.current_target = get_tile_position(self.path[self.path_index][0], 
                                                                   self.path[self.path_index][1])
                            self.previous_target_tile = target_tile
                            self.wander_timer = 0
                            print(f"Wander: New target set at {self.current_target}")
                            return
                attempts += 1
            # If no valid target found after max attempts, switch to 'waiting'
            self.state = 'waiting'
            self.speed = 0  # Stop moving
            self.update_color(YELLOW)
            self.waiting_timer = 0
            print("Wander: No valid target found. Switching to 'waiting' state.")
        
        elif state == 'follow':
            print("\nTracker State: Follow")
            self.update_color(GREEN)
            player_tile = (player.rect.centery // TILE_SIZE, player.rect.centerx // TILE_SIZE)
            tracker_tile = (self.rect.centery // TILE_SIZE, self.rect.centerx // TILE_SIZE)
            if player_tile != tracker_tile:
                candidate_path = bfs(map_layout, tracker_tile, player_tile)
                if candidate_path and len(candidate_path) > 1:
                    self.path = candidate_path
                    self.path_index = 1
                    self.current_target = get_tile_position(self.path[self.path_index][0], 
                                                           self.path[self.path_index][1])
                    self.speed = self.follow_speed
                    print(f"Follow: New target set at {self.current_target}")
                else:
                    self.current_target = None
                    print("Follow: No path to player.")
            else:
                self.current_target = None
                print("Follow: Tracker is already on the player's tile.")

    def move_along_path(self, dt):
        if self.current_target is None:
            return
        
        reached = move_towards_target(self, self.current_target, dt)
        if reached:
            self.path_index += 1
            if self.path_index < len(self.path):
                self.current_target = get_tile_position(self.path[self.path_index][0], 
                                                       self.path[self.path_index][1])
                print(f"Tracker: Moving to next path tile index {self.path_index}, target {self.current_target}")
            else:
                if self.state == 'wander':
                    print("Wander: Reached end of path. Selecting new wander target.")
                    self.current_target = None
                elif self.state == 'follow':
                    print("Follow: Reached end of path.")
                    self.initialize_tracker_target('follow', map_layout, walkable_tiles)

    def update_color(self, color):
        if self.color != color:
            self.color = color
            self.image.fill(self.color)

# BFS for shortest path
def bfs(map_layout, start, goal):
    rows, cols = len(map_layout), len(map_layout[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
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
            print(f"BFS: Path found from {start} to {goal}: {path}")
            return path[::-1]  # Return path from start to goal

        for d in directions:
            nx, ny = current[0] + d[0], current[1] + d[1]
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited and map_layout[nx][ny] == " ":
                queue.append((nx, ny))
                visited.add((nx, ny))
                parent[(nx, ny)] = current

    print(f"BFS: No path found from {start} to {goal}")
    return []  # If no path found, return empty path

# Move towards target with smooth movement
def move_towards_target(character, target, dt):
    dx = target[0] - character.rect.centerx
    dy = target[1] - character.rect.centery
    distance = math.hypot(dx, dy)

    if distance < 5:
        return True  # Reached target
    else:
        move_x = (dx / distance) * character.speed * dt
        move_y = (dy / distance) * character.speed * dt

        # Prevent overshooting
        if abs(move_x) > abs(dx):
            move_x = dx
        if abs(move_y) > abs(dy):
            move_y = dy

        character.rect.x += move_x
        character.rect.y += move_y
        return False  # Still moving

# Create wall sprites and collect walkable tiles
walls = pygame.sprite.Group()
walkable_tiles = []  # List to store all walkable tile positions
for row_idx, row in enumerate(map_layout):
    for col_idx, tile in enumerate(row):
        if tile == 'W':
            walls.add(Wall(col_idx * TILE_SIZE, row_idx * TILE_SIZE))
        elif tile == ' ':
            # Store the center position of walkable tiles for random target selection
            center_x = col_idx * TILE_SIZE + TILE_SIZE // 2
            center_y = row_idx * TILE_SIZE + TILE_SIZE // 2
            walkable_tiles.append((row_idx, col_idx, center_x, center_y))

# Ensure there are enough walkable tiles to place player and tracker
if len(walkable_tiles) < 2:
    raise ValueError("Not enough walkable tiles to place both player and tracker.")

# Randomly select two distinct walkable tiles for player and tracker
player_tile, tracker_tile = random.sample(walkable_tiles, 2)

# Initialize Player and Tracker with respective speeds
player = Player(player_tile[2], player_tile[3], RED, speed=150)      # Player (Red Ball)
tracker = Tracker(tracker_tile[2], tracker_tile[3], BLUE, WANDER_SPEED, FOLLOW_SPEED, VISIBILITY_RADIUS)  # Tracker starts in 'wander' state

# Create the radial gradient surface
def create_radial_gradient(radius, fade_color_alpha=180):
    """
    Creates a radial gradient surface with a transparent center and
    increasing opacity towards the edges.

    :param radius: Radius of the gradient in pixels.
    :param fade_color_alpha: Maximum alpha value at the edges.
    :return: A Pygame Surface with the radial gradient.
    """
    size = radius * 2
    gradient_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    for i in range(radius, 0, -1):
        alpha = int((1 - i / radius) * fade_color_alpha)
        pygame.draw.circle(gradient_surface, (0, 0, 0, alpha), (radius, radius), i)
    
    return gradient_surface

# Initialize the gradient surface
visibility_gradient = create_radial_gradient(VISIBILITY_RADIUS)

# Create darkness overlay
darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
darkness.fill((0, 0, 0, 180))  # Semi-transparent black (alpha=180)

# Function to update the darkness overlay with the gradient
def update_darkness(player_pos):
    darkness.fill((0, 0, 0, 180))  # Reset darkness to semi-transparent black
    # Calculate top-left position to blit the gradient
    gradient_pos = (player_pos[0] - VISIBILITY_RADIUS, player_pos[1] - VISIBILITY_RADIUS)
    # Blit the gradient onto the darkness overlay using subtraction blending
    darkness.blit(visibility_gradient, gradient_pos, special_flags=pygame.BLEND_RGBA_SUB)

# Function to visualize the current path (Optional)
def draw_path(path_list):
    if path_list:
        for tile in path_list:
            pos = get_tile_position(tile[0], tile[1])
            pygame.draw.circle(screen, (0, 255, 0), pos, 5)  # Small green circles for path tiles

# Main loop setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Tracker Behavior with Realistic Fog")
clock = pygame.time.Clock()
running = True

def get_tile_position(tile_row, tile_col):
    """Convert tile coordinates to pixel center position."""
    center_x = tile_col * TILE_SIZE + TILE_SIZE // 2
    center_y = tile_row * TILE_SIZE + TILE_SIZE // 2
    return (center_x, center_y)

# Initialize tracker target
tracker.initialize_tracker_target('wander', map_layout, walkable_tiles)

while running:
    dt = clock.tick(FPS) / 1000  # Delta time in seconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle player movement
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

    # Calculate potential new position
    new_player_x = player.rect.x + dx * player.speed * dt
    new_player_y = player.rect.y + dy * player.speed * dt

    # Create a rect for the new position to check collisions
    new_player_rect = player.rect.copy()
    new_player_rect.x = new_player_x
    new_player_rect.y = new_player_y

    # Check collision with walls
    collision = any(wall.rect.colliderect(new_player_rect) for wall in walls)
    if not collision:
        player.rect.x = new_player_x
        player.rect.y = new_player_y

    # Calculate distance between player and tracker
    distance = math.hypot(player.rect.centerx - tracker.rect.centerx, player.rect.centery - tracker.rect.centery)

    # State transition based on distance
    if distance > DISTANCE_THRESHOLD and tracker.state != 'wander':
        tracker.state = 'wander'
        tracker.speed = tracker.wander_speed  # Set speed for wandering
        print("\nState change: wander")
        tracker.initialize_tracker_target('wander', map_layout, walkable_tiles)
    elif distance <= DISTANCE_THRESHOLD and tracker.state != 'follow':
        tracker.state = 'follow'
        tracker.speed = tracker.follow_speed  # Set speed for following
        print("\nState change: follow")
        tracker.initialize_tracker_target('follow', map_layout, walkable_tiles)

    # Update tracker
    tracker.update(dt, player.rect.center, map_layout, walkable_tiles)

    # Draw everything
    screen.fill(WHITE)
    walls.draw(screen)
    screen.blit(player.image, player.rect)
    screen.blit(tracker.image, tracker.rect)

    # Optional: Draw the current path for debugging
    # draw_path(tracker.path)

    # Update and blit the darkness overlay with the gradient
    update_darkness(player.rect.center)
    screen.blit(darkness, (0, 0))

    pygame.display.flip()

pygame.quit()
