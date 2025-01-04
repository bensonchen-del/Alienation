# rendering.py
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
