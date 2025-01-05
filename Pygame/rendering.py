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
