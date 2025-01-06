import math
import pygame
from game_objects import get_tile_position
from config import *

def create_radial_gradient(base_radius, time_factor, fade_color_alpha=180):
    pulsation = int(10 * math.sin(time_factor))  # Pulsates between -10 and +10
    radius = base_radius + pulsation
    size = radius * 2
    gradient_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    for i in range(radius, 0, -1):
        alpha = int((1 - i / radius) * fade_color_alpha)
        pygame.draw.circle(gradient_surface, (0, 0, 0, alpha), (radius, radius), i)
    return gradient_surface

screen = pygame.display.set_mode((WIDTH, HEIGHT))

def draw_path(path_list):
    if path_list:
        for tile in path_list:
            pos = get_tile_position(tile[0], tile[1])
            pygame.draw.circle(screen, (0, 255, 0), pos, 5)  # Small green circles for path tiles

def update_darkness(player_pos, visibility_gradient, darkness, time_factor):
    # Clear the darkness surface
    darkness.fill((0, 0, 0, 255))  # Fully opaque black background

    # Create a swirling offset for the fog
    offset_x = int(10 * math.sin(time_factor / 2))  # Sway horizontally
    offset_y = int(10 * math.cos(time_factor / 2))  # Sway vertically
    gradient_pos = (player_pos[0] - VISIBILITY_RADIUS + offset_x, 
                    player_pos[1] - VISIBILITY_RADIUS + offset_y)

    # Position the gradient around the player
    darkness.blit(visibility_gradient, gradient_pos, special_flags=pygame.BLEND_RGBA_SUB)

def draw_radar(screen, player_pos, tracker_pos, radar_center, radar_radius, sweep_angle, max_radar_distance=500, trail_length=10):
    # Create a radar surface with per-pixel alpha
    radar_surface = pygame.Surface((radar_radius * 2, radar_radius * 2), pygame.SRCALPHA)
    # No need to set overall alpha; use per-pixel alpha instead

    # Draw radar background first
    pygame.draw.circle(radar_surface, (0, 50, 0, 200), (radar_radius, radar_radius), radar_radius)
    for i in range(1, 5):  # Draw concentric circles
        pygame.draw.circle(radar_surface, (0, 100, 0, 200), (radar_radius, radar_radius), radar_radius * i // 5, 1)
    
    # Player position with green dot
    pygame.draw.circle(radar_surface, (0, 255, 0, 255), (radar_radius, radar_radius), 5)

    # Calculate tracker position
    dx = tracker_pos[0] - player_pos[0]
    dy = tracker_pos[1] - player_pos[1]
    distance = math.hypot(dx, dy)

    if 0 < distance <= max_radar_distance:  # Limit tracker display range
        direction_x = dx / distance
        direction_y = dy / distance
        scaled_distance = min(distance / max_radar_distance * radar_radius, radar_radius)

        tracker_radar_x = radar_radius + direction_x * scaled_distance
        tracker_radar_y = radar_radius + direction_y * scaled_distance

        # Tracker position with white dot
        pygame.draw.circle(radar_surface, (255, 255, 255, 255), (int(tracker_radar_x), int(tracker_radar_y)), 7)

    # Draw the sweeping line and its fading trail
    # Define trail_length (number of trailing lines) and trail_spacing (degrees between them)
    trail_length = 50  # Adjust as needed for desired trail length
    trail_spacing = 0.75   # Degrees between trailing lines

    for i in range(trail_length):
        # Calculate the angle for each trailing line
        angle = sweep_angle - i * trail_spacing
        angle_rad = math.radians(angle)
        end_x = radar_radius + radar_radius * math.cos(angle_rad)
        end_y = radar_radius + radar_radius * math.sin(angle_rad)
        
        # Calculate alpha for fading effect
        alpha = min(50 + i * 3, 255)  # Decrease alpha for trail
        sweep_color = (50, 50, 50, alpha)  # Semi-transparent white
        
        # Draw the trailing line
        pygame.draw.line(radar_surface, sweep_color, (radar_radius, radar_radius), (end_x, end_y), 2)

    # Blit the radar surface to the main screen
    screen.blit(radar_surface, (radar_center[0] - radar_radius, radar_center[1] - radar_radius))
