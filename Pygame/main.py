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

def calculate_distance(pos1, pos2):
    """Calculate Euclidean distance between two positions."""
    return math.hypot(pos2[0] - pos1[0], pos2[1] - pos1[1])

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

    # Locate goal tile (marked as 'G' in the map)
    goal_tile = None
    for row_idx, row in enumerate(map_layout):
        for col_idx, tile in enumerate(row):
            if tile == 'G':
                goal_tile = (col_idx * TILE_SIZE + TILE_SIZE // 2, row_idx * TILE_SIZE + TILE_SIZE // 2)
                break

    if not goal_tile:
        raise ValueError("No goal ('G') found in the map.")

    # Spawn player and tracker with minimum distance constraint
    while True:
        player_tile, tracker_tile = random.sample(walkable_tiles, 2)
        player_pos = (player_tile[2], player_tile[3])
        tracker_pos = (tracker_tile[2], tracker_tile[3])

        # Ensure player and tracker are far enough apart
        if calculate_distance(player_pos, tracker_pos) > TILE_SIZE * 8:
            # Ensure player and goal are far enough apart
            if calculate_distance(player_pos, goal_tile) > TILE_SIZE * 12:
                break

    # Initialize player and tracker
    player = Player(player_tile[2], player_tile[3], RED, speed=150)
    tracker = Tracker(tracker_tile[2], tracker_tile[3], BLUE, WANDER_SPEED, FOLLOW_SPEED, VISIBILITY_RADIUS)

    return map_layout

# Load goal tile image
goal_image = pygame.image.load("assets/door.png")

def draw_goal_tile():
    """Draw the goal tile at its position."""
    if goal_tile:
        goal_rect = goal_image.get_rect(center=goal_tile)
        screen.blit(goal_image, goal_rect)

# Initialize first level
map_layout = load_level(current_level_index)

walls, walkable_tiles = create_map(map_layout)

def game_over_screen():
    """Display the Game Over screen and allow the user to restart or quit."""
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)
    screen.fill((0, 0, 0))

    # Render text
    text = font.render("Game Over", True, (255, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

    restart_text = small_font.render("Press R to Restart", True, (255, 255, 255))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))

    quit_text = small_font.render("Press Q to Quit", True, (255, 255, 255))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 60))

    pygame.display.flip()

    # Wait for user input
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart the game
                    return True
                elif event.key == pygame.K_q:  # Quit the game
                    pygame.quit()
                    sys.exit()

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
    if pygame.sprite.collide_rect(player, tracker):
        screen.fill((0, 0, 0))  # Clear screen
        screen.blit(jumpscare_image, (WIDTH // 2 - jumpscare_image.get_width() // 2, HEIGHT // 2 - jumpscare_image.get_height() // 2))
        game_over = game_over_screen()  # Display Game Over screen
        if game_over:
            current_level_index = 0  # Reset to the first level
            map_layout = load_level(current_level_index)  # Reload the first level
            player.rect.topleft = (walkable_tiles[0][2], walkable_tiles[0][3])  # Reset player position
            tracker.rect.topleft = (walkable_tiles[1][2], walkable_tiles[1][3])  # Reset tracker position

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
