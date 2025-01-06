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

def draw_radar(screen, player_pos, tracker_pos, radar_center, radar_radius, sweep_angle, max_radar_distance=500):
    # Create a radar surface with transparency
    radar_surface = pygame.Surface((radar_radius * 2, radar_radius * 2), pygame.SRCALPHA)
    radar_surface.set_alpha(200)  # Set transparency (0 fully transparent, 255 fully opaque)

    # Draw radar background
    pygame.draw.circle(radar_surface, GREEN_DARK + (200,), (radar_radius, radar_radius), radar_radius)
    
    # Draw concentric circles
    for i in range(1, 5):
        pygame.draw.circle(radar_surface, GREEN_MEDIUM + (200,), (radar_radius, radar_radius), radar_radius * i // 5, 1)
    
    # Draw player position as a green dot at the center
    pygame.draw.circle(radar_surface, GREEN_LIGHT + (255,), (radar_radius, radar_radius), 5)
    
    # Calculate tracker position relative to player
    dx = tracker_pos[0] - player_pos[0]
    dy = tracker_pos[1] - player_pos[1]
    distance = math.hypot(dx, dy)

    if 0 < distance <= max_radar_distance:
        direction_x = dx / distance
        direction_y = dy / distance
        scaled_distance = min(distance / max_radar_distance * radar_radius, radar_radius)

        tracker_radar_x = radar_radius + direction_x * scaled_distance
        tracker_radar_y = radar_radius + direction_y * scaled_distance

        # Draw tracker position as a white dot
        pygame.draw.circle(radar_surface, WHITE + (255,), (int(tracker_radar_x), int(tracker_radar_y)), 7)
    
    # Draw the sweeping line
    # Convert angle from degrees to radians
    angle_rad = math.radians(sweep_angle)
    
    # Calculate the end point of the sweep line
    end_x = radar_radius + radar_radius * math.cos(angle_rad)
    end_y = radar_radius + radar_radius * math.sin(angle_rad)
    
    # Draw the sweep line with a semi-transparent color
    pygame.draw.line(radar_surface, WHITE + (150,), (radar_radius, radar_radius), (end_x, end_y), 2)
    
    # Optional: Add a fading effect to the sweep line
    # You can achieve this by drawing a semi-transparent arc or using gradients

    # Blit the radar surface onto the main screen
    screen.blit(radar_surface, (radar_center[0] - radar_radius, radar_center[1] - radar_radius))
    # 創建一個帶透明度的雷達表面
    radar_surface = pygame.Surface((radar_radius * 2, radar_radius * 2), pygame.SRCALPHA)
    radar_surface.set_alpha(200)  # 設置透明度（0 完全透明，255 完全不透明）

    # 雷達背景設置為深綠色
    pygame.draw.circle(radar_surface, (0, 50, 0, 200), (radar_radius, radar_radius), radar_radius)
    for i in range(1, 5):  # 繪製同心圓
        pygame.draw.circle(radar_surface, (0, 100, 0, 200), (radar_radius, radar_radius), radar_radius * i // 5, 1)
    
    # 玩家位置用綠色圓點表示
    pygame.draw.circle(radar_surface, (0, 255, 0, 255), (radar_radius, radar_radius), 5)

    # 計算追蹤者位置
    dx = tracker_pos[0] - player_pos[0]
    dy = tracker_pos[1] - player_pos[1]
    distance = math.hypot(dx, dy)

    if distance > 0 and distance <= max_radar_distance:  # 限制追蹤者顯示範圍
        direction_x = dx / distance
        direction_y = dy / distance
        scaled_distance = min(distance / max_radar_distance * radar_radius, radar_radius)

        tracker_radar_x = radar_radius + direction_x * scaled_distance
        tracker_radar_y = radar_radius + direction_y * scaled_distance

        # 追蹤者位置用白色點表示
        pygame.draw.circle(radar_surface, (255, 255, 255, 255), (int(tracker_radar_x), int(tracker_radar_y)), 7)

    # 將雷達表面繪製到主屏幕上
    screen.blit(radar_surface, (radar_center[0] - radar_radius, radar_center[1] - radar_radius))