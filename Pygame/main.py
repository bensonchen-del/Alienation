import pygame
import random
import math
from config import *
from map_resources import load_map, create_map
from game_objects import Player, Tracker
from rendering import create_radial_gradient, update_darkness

pygame.init()

# Load map and initialize resources
map_layout = load_map("Pygame/map/map1.txt")
walls, walkable_tiles = create_map(map_layout)

# Initialize player and tracker
player_tile, tracker_tile = random.sample(walkable_tiles, 2)
player = Player(player_tile[2], player_tile[3], RED, speed=150)
tracker = Tracker(tracker_tile[2], tracker_tile[3], BLUE, WANDER_SPEED, FOLLOW_SPEED, VISIBILITY_RADIUS)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Tracker Behavior with Realistic Fog")
clock = pygame.time.Clock()
visibility_gradient = create_radial_gradient(VISIBILITY_RADIUS)
darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

running = True
while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    current_speed = RUN_SPEED if keys[pygame.K_SPACE] else SNEAK_SPEED if keys[pygame.K_c] else player.speed

    dx, dy = 0, 0
    if keys[pygame.K_w]: dy = -1
    if keys[pygame.K_s]: dy = 1
    if keys[pygame.K_a]: dx = -1
    if keys[pygame.K_d]: dx = 1

    new_player_x = player.rect.x + dx * current_speed * dt
    new_player_y = player.rect.y + dy * current_speed * dt

    new_player_rect = player.rect.copy()
    new_player_rect.x = new_player_x
    new_player_rect.y = new_player_y

    # Check collision
    collision = any(wall.rect.colliderect(new_player_rect) for wall in walls)
    if not collision:
        player.rect.x = new_player_x
        player.rect.y = new_player_y

    # Calculate distance to player
    distance = math.hypot(player.rect.centerx - tracker.rect.centerx, player.rect.centery - tracker.rect.centery)

    # Update tracker state
    if distance > DISTANCE_THRESHOLD and tracker.state != 'wander':
        tracker.state = 'wander'
        tracker.speed = tracker.wander_speed
        tracker.initialize_tracker_target('wander', map_layout, walkable_tiles, player)
    elif distance <= DISTANCE_THRESHOLD and tracker.state != 'follow':
        tracker.state = 'follow'
        tracker.speed = tracker.follow_speed
        tracker.initialize_tracker_target('follow', map_layout, walkable_tiles, player)

    tracker.update(dt, player.rect.center, map_layout, walkable_tiles, player)

    # Rendering
    screen.fill(WHITE)
    walls.draw(screen)
    screen.blit(player.image, player.rect)
    screen.blit(tracker.image, tracker.rect)
    update_darkness(player.rect.center, visibility_gradient, darkness)
    screen.blit(darkness, (0, 0))
    pygame.display.flip()

pygame.quit()
