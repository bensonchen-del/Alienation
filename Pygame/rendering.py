# rendering.py
import math
from turtle import Screen
import pygame
from game_objects import get_tile_position
from config import *


def create_radial_gradient(radius, fade_color_alpha=180):
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

def update_darkness(player_pos, visibility_gradient, darkness):
    darkness.fill((0, 0, 0, 0))
    gradient_pos = (player_pos[0] - VISIBILITY_RADIUS, player_pos[1] - VISIBILITY_RADIUS)
    darkness.blit(visibility_gradient, gradient_pos, special_flags=pygame.BLEND_RGBA_SUB)

def draw_radar(screen, player_pos, tracker_pos, radar_center, radar_radius):
    # Draw radar background
    pygame.draw.circle(screen, (50, 50, 50), radar_center, radar_radius)
    for i in range(1, 5):  # Concentric circles
        pygame.draw.circle(screen, (100, 100, 100), radar_center, radar_radius * i // 5, 1)
    
    # Player position
    pygame.draw.circle(screen, (0, 255, 0), radar_center, 5)
    
    # Calculate tracker position
    dx = tracker_pos[0] - player_pos[0]
    dy = tracker_pos[1] - player_pos[1]
    distance = math.hypot(dx, dy)
    
    # Normalize direction and scale to radar size
    if distance > 0:
        direction_x = dx / distance
        direction_y = dy / distance
        scaled_distance = min(distance / 500 * radar_radius, radar_radius)  # Scale to radar radius
        
        tracker_radar_x = radar_center[0] + direction_x * scaled_distance
        tracker_radar_y = radar_center[1] + direction_y * scaled_distance
        
        # Draw tracker
        pygame.draw.circle(screen, (255, 0, 0), (int(tracker_radar_x), int(tracker_radar_y)), 5)
        
        # Add line for direction
        pygame.draw.line(screen, (255, 0, 0), radar_center, (int(tracker_radar_x), int(tracker_radar_y)), 1)

