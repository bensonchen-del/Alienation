import pygame
import random
import math
import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from config import *
from map_resources import load_map, create_map
from game_objects import Player, Tracker
from rendering import create_radial_gradient, update_darkness, draw_path, draw_radar

pygame.init()

# Load map and initialize resources
#map_layout = load_map("map/map1.txt")
# Load all maps for levels
LEVELS = [f"map/map{i + 1}.txt" for i in range(5)]
current_level_index = 0

def load_level(level_index):
    """Load the map and initialize level resources."""
    global walls, walkable_tiles, player, tracker, goal_tile
    map_layout = load_map(LEVELS[level_index])
    walls, walkable_tiles = create_map(map_layout)

    # Initialize player and tracker
    player_tile, tracker_tile = random.sample(walkable_tiles, 2)
    player = Player(player_tile[2], player_tile[3], RED, speed=150)
    tracker = Tracker(tracker_tile[2], tracker_tile[3], BLUE, WANDER_SPEED, FOLLOW_SPEED, VISIBILITY_RADIUS)

    # Locate goal tile
    for row_idx, row in enumerate(map_layout):
        for col_idx, tile in enumerate(row):
            if tile == 'G':
                goal_tile = (col_idx * TILE_SIZE + TILE_SIZE // 2, row_idx * TILE_SIZE + TILE_SIZE // 2)
                break

    return map_layout

# Load goal tile image
goal_image = pygame.image.load("assets/door.png")

def draw_goal_tile():
    """Draw the goal tile at its position."""
    if goal_tile:
        goal_rect = goal_image.get_rect(center=(goal_tile[0], goal_tile[1]))
        screen.blit(goal_image, goal_rect)

# Initialize first level
map_layout = load_level(current_level_index)

walls, walkable_tiles = create_map(map_layout)

# Initialize player and tracker
player_tile, tracker_tile = random.sample(walkable_tiles, 2)
player = Player(player_tile[2], player_tile[3], RED, speed=150)
tracker = Tracker(tracker_tile[2], tracker_tile[3], BLUE, WANDER_SPEED, FOLLOW_SPEED, VISIBILITY_RADIUS)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Tracker Behavior with Realistic Fog")
clock = pygame.time.Clock()
visibility_gradient = create_radial_gradient(VISIBILITY_RADIUS, 180)
darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Load jumpscare image
jumpscare_image = pygame.image.load("assets/jumpscare1.png")

# Load background sound
pygame.mixer.init()
pygame.mixer.music.load("Deep Fan Noise (1 Minute).mp3")
pygame.mixer.music.play(-1)  # Loop background sound infinitely

time_factor = 0  # Time factor for dynamic effects

sweep_angle = 0

running = True
while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Determine player's movement speed and adjust DISTANCE_THRESHOLD
    if keys[pygame.K_c]:  # Sneak mode
        current_speed = SNEAK_SPEED
        current_distance_threshold = DISTANCE_THRESHOLD * 0.5  # Reduced threshold for sneaking
    elif keys[pygame.K_SPACE]:  # Sprint mode
        current_speed = RUN_SPEED
        current_distance_threshold = DISTANCE_THRESHOLD * 2.5  # Increased threshold for sprinting
    else:  # Normal mode
        current_speed = player.speed
        current_distance_threshold = DISTANCE_THRESHOLD  # Default threshold

    # Adjust distance calculations based on new threshold
    dx, dy = 0, 0
    if keys[pygame.K_w]: dy = -1
    if keys[pygame.K_s]: dy = 1
    if keys[pygame.K_a]: dx = -1
    if keys[pygame.K_d]: dx = 1

    # Normalize diagonal movement
    if dx != 0 and dy != 0:
        dx *= math.sqrt(0.5)
        dy *= math.sqrt(0.5)

    # Update player's position
    new_player_x = player.rect.x + dx * current_speed * dt
    new_player_y = player.rect.y + dy * current_speed * dt

    new_player_rect_x = player.rect.copy()
    new_player_rect_x.x = new_player_x

    new_player_rect_y = player.rect.copy()
    new_player_rect_y.y = new_player_y

    collision_x = any(wall.rect.colliderect(new_player_rect_x) for wall in walls)
    collision_y = any(wall.rect.colliderect(new_player_rect_y) for wall in walls)

    if not collision_x:
        player.rect.x = new_player_x
    if not collision_y:
        player.rect.y = new_player_y

    # Update sweep angle
    sweep_angle = (sweep_angle + SWEEP_SPEED * dt) % 360  # Rotate 1 degree per frame

    # Tracker logic based on adjusted DISTANCE_THRESHOLD
    distance = math.hypot(player.rect.centerx - tracker.rect.centerx, player.rect.centery - tracker.rect.centery)
    if distance > current_distance_threshold and tracker.state != 'wander':
        tracker.state = 'wander'
        tracker.speed = tracker.wander_speed
        tracker.initialize_tracker_target('wander', map_layout, walkable_tiles, player)
    elif distance <= current_distance_threshold and tracker.state != 'follow':
        tracker.state = 'follow'
        tracker.speed = tracker.follow_speed
        tracker.initialize_tracker_target('follow', map_layout, walkable_tiles, player)
    tracker.update(dt, player, map_layout, walkable_tiles)

    # Check for collision between player and tracker
    if pygame.sprite.collide_rect(player, tracker):  # Check if player and tracker collide
        screen.fill((0, 0, 0))  # Clear screen
        screen.blit(jumpscare_image, (WIDTH // 2 - jumpscare_image.get_width() // 2, HEIGHT // 2 - jumpscare_image.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(500)  # Show jumpscare for 0.5 seconds
        pygame.quit()
        sys.exit()

    # Check for level transition
    player_tile = (player.rect.centery // TILE_SIZE, player.rect.centerx // TILE_SIZE)
    for row_idx, row in enumerate(map_layout):
        for col_idx, tile in enumerate(row):
            if tile == 'G' and player_tile == (row_idx, col_idx):
                current_level_index += 1
                if current_level_index < len(LEVELS):
                    map_layout = load_level(current_level_index)
                else:
                    print("You completed all levels!")
                    running = False

    # Rendering
    screen.fill(WHITE)
    walls.draw(screen)
    screen.blit(player.image, player.rect)
    screen.blit(tracker.image, tracker.rect)
    draw_path(tracker.path)

    # In your game loop
    time_factor += dt  # Increment time factor

    # Generate the dynamic visibility gradient
    visibility_gradient = create_radial_gradient(VISIBILITY_RADIUS, time_factor)

    # Update the fog effect
    update_darkness(player.rect.center, visibility_gradient, darkness, time_factor)
    screen.blit(darkness, (0, 0))

    # Draw radar (after main elements)
    draw_radar(screen, player.rect.center, tracker.rect.center, RADAR_CENTER, RADAR_RADIUS, sweep_angle)

    # Draw goal tile
    draw_goal_tile()

    pygame.display.flip()

pygame.quit()
