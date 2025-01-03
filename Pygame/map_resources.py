# map_resources.py
import pygame
from config import TILE_SIZE, BLACK

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))

def load_map(file_path):
    """Load the map from a text file."""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

def create_map(map_layout):
    """Generate wall sprites and collect walkable tiles."""
    walls = pygame.sprite.Group()
    walkable_tiles = []
    for row_idx, row in enumerate(map_layout):
        for col_idx, tile in enumerate(row):
            if tile == 'W':
                walls.add(Wall(col_idx * TILE_SIZE, row_idx * TILE_SIZE))
            elif tile == ' ':
                center_x = col_idx * TILE_SIZE + TILE_SIZE // 2
                center_y = row_idx * TILE_SIZE + TILE_SIZE // 2
                walkable_tiles.append((row_idx, col_idx, center_x, center_y))
    return walls, walkable_tiles
