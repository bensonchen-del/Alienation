import pygame
import math

# Constants
PLAYER_SPEEDS = {'walk': 150, 'run': 300, 'stealth': 75}
ALIEN_SPEED = 200  # pixels per second

# Define Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, image, run_image, stealth_image, x, y):
        super().__init__()
        self.images = {
            'walk': image,
            'run': run_image,
            'stealth': stealth_image
        }
        self.state = 'walk'  # Default state
        self.image = self.images[self.state]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_SPEEDS[self.state]

    def update_state(self, new_state):
        if new_state in self.images:
            self.state = new_state
            self.image = self.images[self.state]
            self.speed = PLAYER_SPEEDS[self.state]

    def move(self, dx, dy, walls):
        # Move horizontally
        self.rect.x += dx
        collided_walls = pygame.sprite.spritecollide(self, walls, False)
        if collided_walls:
            if dx > 0:  # Moving right; align to the left side of the wall
                self.rect.right = collided_walls[0].rect.left
            elif dx < 0:  # Moving left; align to the right side of the wall
                self.rect.left = collided_walls[0].rect.right

        # Move vertically
        self.rect.y += dy
        collided_walls = pygame.sprite.spritecollide(self, walls, False)
        if collided_walls:
            if dy > 0:  # Moving down; align to the top side of the wall
                self.rect.bottom = collided_walls[0].rect.top
            elif dy < 0:  # Moving up; align to the bottom side of the wall
                self.rect.top = collided_walls[0].rect.bottom

        # Optional: Keep the player within the screen bounds
        self.rect.x = max(0, min(self.rect.x, 1600 - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, 1600 - self.rect.height))

class Alien(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = ALIEN_SPEED
        self.last_update_time = 0  # 用於控制路徑更新的時間
        self.path = []  # 保存計算出的路徑
        self.current_target_index = 1  # 路徑中的下一個目標點索引

    def update_position(self, dt, walls, map_layout, player_pos):
        # 定義更新路徑的間隔時間 (毫秒)
        path_update_interval = 500

        # 獲取當前時間
        current_time = pygame.time.get_ticks()

        # 如果路徑需要更新
        if current_time - self.last_update_time > path_update_interval:
            alien_grid_pos = (self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE)
            player_grid_pos = (player_pos[0] // TILE_SIZE, player_pos[1] // TILE_SIZE)
            self.path = find_path(map_layout, alien_grid_pos, player_grid_pos)
            self.last_update_time = current_time
            self.current_target_index = 1  # 重置目標點索引

        # 如果路徑存在，移動到下一個目標點
        if len(self.path) > 1 and self.current_target_index < len(self.path):
            next_pos = self.path[self.current_target_index]
            next_x = next_pos[0] * TILE_SIZE + TILE_SIZE // 2
            next_y = next_pos[1] * TILE_SIZE + TILE_SIZE // 2

            dx = next_x - self.rect.centerx
            dy = next_y - self.rect.centery
            distance = math.hypot(dx, dy)

            if distance != 0:
                move_x = (dx / distance) * self.speed * dt
                move_y = (dy / distance) * self.speed * dt
                self.rect.x += move_x
                self.rect.y += move_y

            # 如果到達目標點，更新索引
            if abs(dx) < 5 and abs(dy) < 5:
                self.current_target_index += 1

