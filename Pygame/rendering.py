# rendering.py
import math
from turtle import Screen
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

<<<<<<< HEAD
def update_darkness(player_pos, visibility_gradient, darkness):
    darkness.fill((0, 0, 0, 180))
    gradient_pos = (player_pos[0] - VISIBILITY_RADIUS, player_pos[1] - VISIBILITY_RADIUS)
    darkness.blit(visibility_gradient, gradient_pos, special_flags=pygame.BLEND_RGBA_SUB)

def draw_radar(screen, player_pos, tracker_pos, radar_center, radar_radius, max_radar_distance=500):
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
=======
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

def draw_radar(screen, player_pos, tracker_pos, radar_center, radar_radius):
    # Create a transparent surface for the radar
    radar_surface = pygame.Surface((radar_radius * 2, radar_radius * 2), pygame.SRCALPHA)
    radar_surface.fill((0, 0, 0, 0))  # Fully transparent background

    # Draw radar background on the transparent surface
    pygame.draw.circle(radar_surface, (50, 50, 50, 150), (radar_radius, radar_radius), radar_radius)  # Semi-transparent gray
    for i in range(1, 5):  # Concentric circles
        pygame.draw.circle(radar_surface, (100, 100, 100, 100), (radar_radius, radar_radius), radar_radius * i // 5, 1)
    
    # Player position (center of radar)
    pygame.draw.circle(radar_surface, (0, 255, 0, 255), (radar_radius, radar_radius), 5)  # Opaque green dot for player

    # Calculate tracker position relative to player
>>>>>>> deb4dd959f5a4fbb0fd12b8350c1a261c2d12ec7
    dx = tracker_pos[0] - player_pos[0]
    dy = tracker_pos[1] - player_pos[1]
    distance = math.hypot(dx, dy)

<<<<<<< HEAD
    if distance > 0 and distance <= max_radar_distance:  # 限制追蹤者顯示範圍
        direction_x = dx / distance
        direction_y = dy / distance
        scaled_distance = min(distance / max_radar_distance * radar_radius, radar_radius)

        tracker_radar_x = radar_radius + direction_x * scaled_distance
        tracker_radar_y = radar_radius + direction_y * scaled_distance

        # 追蹤者位置用白色點表示
        pygame.draw.circle(radar_surface, (255, 255, 255, 255), (int(tracker_radar_x), int(tracker_radar_y)), 7)

    # 將雷達表面繪製到主屏幕上
=======
    if distance > 0:
        direction_x = dx / distance
        direction_y = dy / distance
        scaled_distance = min(distance / 500 * radar_radius, radar_radius)  # Scale to radar radius
        tracker_x = radar_radius + direction_x * scaled_distance
        tracker_y = radar_radius + direction_y * scaled_distance

        # Draw tracker position and direction line
        pygame.draw.circle(radar_surface, (255, 0, 0, 255), (int(tracker_x), int(tracker_y)), 5)  # Opaque red dot for tracker
        pygame.draw.line(radar_surface, (255, 0, 0, 150), (radar_radius, radar_radius), (int(tracker_x), int(tracker_y)), 1)

    # Blit the radar surface onto the main screen
>>>>>>> deb4dd959f5a4fbb0fd12b8350c1a261c2d12ec7
    screen.blit(radar_surface, (radar_center[0] - radar_radius, radar_center[1] - radar_radius))
