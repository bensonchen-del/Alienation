# game_objects.py
import pygame
import random
from config import *
from game_logic import bfs, move_towards_target

# 計算瓦片的像素中心位置
def get_tile_position(tile_row, tile_col):
    center_x = tile_col * TILE_SIZE + TILE_SIZE // 2
    center_y = tile_row * TILE_SIZE + TILE_SIZE // 2
    return (center_x, center_y)

# 定義玩家角色
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

# 定義追蹤者角色
class Tracker(pygame.sprite.Sprite):
    def __init__(self, x, y, color, wander_speed, follow_speed, visibility_radius):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.wander_speed = wander_speed
        self.follow_speed = follow_speed
        self.visibility_radius = visibility_radius
        self.state = 'wander'  # 初始狀態
        self.current_target = None  # 當前目標
        self.path = []  # 當前路徑
        self.path_index = 0  # 路徑索引
        self.wander_timer = 0  # 游蕩計時器
        self.waiting_timer = 0  # 等待計時器
        self.previous_target_tile = None  # 前一個目標瓦片
        self.speed = self.wander_speed

    # 初始化追蹤者目標
    def initialize_tracker_target(self, state, map_layout, walkable_tiles, player):
        if state == 'wander':
            attempts = 0
            while attempts < 100:
                tile = random.choice(walkable_tiles)
                target_tile = (tile[0], tile[1])
                current_tile = (self.rect.centery // TILE_SIZE, self.rect.centerx // TILE_SIZE)
                ## print(f"Attempt {attempts}: Target {target_tile}, Current {current_tile}")  # Debug ##
                if target_tile != current_tile:
                    candidate_path = bfs(map_layout, current_tile, target_tile)
                    if candidate_path and len(candidate_path) > 1:
                        self.path = candidate_path
                        self.path_index = 1
                        self.current_target = get_tile_position(self.path[self.path_index][0], 
                                                                self.path[self.path_index][1])
                        print(f"Wander target selected: {self.current_target}")  # Debug
                        return
                attempts += 1
            print("Wander: No valid target found after 100 attempts")
            self.state = 'waiting'
        elif state == 'follow':
            player_tile = (player.rect.centery // TILE_SIZE, player.rect.centerx // TILE_SIZE)
            tracker_tile = (self.rect.centery // TILE_SIZE, self.rect.centerx // TILE_SIZE)
            if player_tile != tracker_tile:
                candidate_path = bfs(map_layout, tracker_tile, player_tile)
                if candidate_path and len(candidate_path) > 1:
                    self.path = candidate_path
                    self.path_index = 1
                    self.current_target = get_tile_position(self.path[self.path_index][0], 
                                                            self.path[self.path_index][1])
                    print(f"Follow target set: {self.current_target}")  # Debug
                else:
                    print("Follow: No path to player")
                    self.current_target = None

    # 更新追蹤者狀態和行為
    def update(self, dt, player_pos, map_layout, walkable_tiles, player):
        print(f"Updating Tracker - State: {self.state}, Current Target: {self.current_target}")  # Debug
        if self.state == 'wander':
            self.wander_timer += dt
            if self.current_target is None:
                self.initialize_tracker_target('wander', map_layout, walkable_tiles, player)
            else:
                reached = move_towards_target(self, self.current_target, dt)
                if reached:
                    self.current_target = None
        elif self.state == 'follow':
            if self.current_target is None:
                self.initialize_tracker_target('follow', map_layout, walkable_tiles, player)
            else:
                reached = move_towards_target(self, self.current_target, dt)
                if reached:
                    self.current_target = None
        elif self.state == 'waiting':
            self.waiting_timer += dt
            if self.waiting_timer >= WAITING_DURATION:
                print("Waiting: Switching back to 'wander'")
                self.state = 'wander'
                self.waiting_timer = 0
                self.initialize_tracker_target('wander', map_layout, walkable_tiles, player)