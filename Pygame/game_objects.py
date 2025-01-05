import math
import pygame
import random
from config import *
from game_logic import bfs, move_towards_target
from map_resources import load_map, create_map

map_layout = load_map("map/map1.txt")

# Calculate the center position of a tile in pixels
def get_tile_position(tile_row, tile_col):
    center_x = tile_col * TILE_SIZE + TILE_SIZE // 2
    center_y = tile_row * TILE_SIZE + TILE_SIZE // 2
    return (center_x, center_y)

# Define the Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

# Define the Tracker class
class Tracker(pygame.sprite.Sprite):
    def __init__(self, x, y, color, wander_speed, follow_speed, visibility_radius):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2))
        self.color = color
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(x, y))
        self.wander_speed = wander_speed
        self.follow_speed = follow_speed
        self.visibility_radius = visibility_radius
        self.state = 'wander'  # Possible states: 'wander', 'follow', 'waiting'
        self.current_target = None
        self.path = []
        self.path_index = 0
        self.wander_timer = 0
        self.waiting_timer = 0
        self.previous_target_tile = None  # To prevent backtracking
        self.speed = self.wander_speed
        self.teleport_timer = 0


    def initialize_tracker_target(self, state, map_layout, walkable_tiles, player=None):
        if state == 'wander':
            print("\nTracker State: Wander")
            self.update_color(BLUE)
            attempts = 0
            max_attempts = 100
            while attempts < max_attempts:
                tile = random.choice(walkable_tiles)
                target_tile = (tile[0], tile[1])
                current_tile = (self.rect.centery // TILE_SIZE, self.rect.centerx // TILE_SIZE)
                if target_tile != current_tile and target_tile != self.previous_target_tile:
                    candidate_path = bfs(map_layout, current_tile, target_tile)
                    if candidate_path and len(candidate_path) > 1:
                        target_pos = get_tile_position(candidate_path[-1][0], candidate_path[-1][1])
                        distance = math.hypot(target_pos[0] - self.rect.centerx,
                                              target_pos[1] - self.rect.centery)
                        if distance >= MIN_TARGET_DISTANCE:
                            self.path = candidate_path
                            self.path_index = 1
                            self.current_target = get_tile_position(
                                self.path[self.path_index][0],
                                self.path[self.path_index][1]
                            )
                            self.previous_target_tile = target_tile
                            self.wander_timer = 0
                            print(f"Wander: New target set at {self.current_target}")
                            return
                attempts += 1
            # If no valid target found after max attempts, switch to 'waiting'
            self.state = 'waiting'
            self.speed = 0  # Stop moving
            self.update_color(YELLOW)
            self.waiting_timer = 0
            print("Wander: No valid target found. Switching to 'waiting' state.")

        elif state == 'follow' and player:
            print("\nTracker State: Follow")
            self.update_color(GREEN)
            player_tile = (player.rect.centery // TILE_SIZE, player.rect.centerx // TILE_SIZE)
            tracker_tile = (self.rect.centery // TILE_SIZE, self.rect.centerx // TILE_SIZE)
            if player_tile != tracker_tile:
                candidate_path = bfs(map_layout, tracker_tile, player_tile)
                if candidate_path and len(candidate_path) > 1:
                    self.path = candidate_path
                    self.path_index = 1
                    self.current_target = get_tile_position(
                        self.path[self.path_index][0],
                        self.path[self.path_index][1]
                    )
                    self.speed = self.follow_speed
                    print(f"Follow: New target set at {self.current_target}")
                else:
                    self.current_target = None
                    print("Follow: No path to player.")
            else:
                self.current_target = None
                print("Follow: Tracker is already on the player's tile.")

    # Add this method in the Tracker class
    def teleport_to_random_tile(self, walkable_tiles):
        random_tile = random.choice(walkable_tiles)
        self.rect.centerx = random_tile[2]
        self.rect.centery = random_tile[3]
        self.current_target = None
        self.path = []
        print(f"Tracker teleported to {self.rect.center}")

    def move_along_path(self, dt):
        if self.current_target is None:
            return False

        reached = move_towards_target(self, self.current_target, dt)
        if reached:
            self.path_index += 1
            if self.path_index < len(self.path):
                self.current_target = get_tile_position(
                    self.path[self.path_index][0],
                    self.path[self.path_index][1]
                )
                print(f"Tracker: Moving to next path tile index {self.path_index}, target {self.current_target}")
            else:
                if self.state == 'wander':
                    print("Wander: Reached end of path. Selecting new wander target.")
                    self.current_target = None
                elif self.state == 'follow':
                    print("Follow: Reached end of path.")
                    self.current_target = None
            return True
        return False

    def update_color(self, color):
        if self.color != color:
            self.color = color
            self.image.fill(self.color)

    def update(self, dt, player, map_layout, walkable_tiles):
        # Update based on state
        print(f"Updating Tracker - State: {self.state}, Current Target: {self.current_target}")  # Debug

        if self.state == 'wander':
            self.wander_timer += dt
            if self.wander_timer >= WANDER_INTERVAL or self.current_target is None:
                print(f"Wander: {WANDER_INTERVAL} seconds elapsed or no current target. Selecting new target.")
                self.initialize_tracker_target('wander', map_layout, walkable_tiles)
            
            if self.current_target:
                self.move_along_path(dt)

        elif self.state == 'follow':
            if self.current_target is None:
                self.initialize_tracker_target('follow', map_layout, walkable_tiles, player)
            else:
                self.move_along_path(dt)

        elif self.state == 'waiting':
            self.waiting_timer += dt
            if self.waiting_timer >= WAITING_DURATION:
                print("Waiting: Switching back to 'wander' state.")
                self.state = 'wander'
                self.speed = self.wander_speed
                self.update_color(BLUE)
                self.waiting_timer = 0
                self.initialize_tracker_target('wander', map_layout, walkable_tiles)

        # Teleport only if not in 'follow' state
        if self.state != 'follow':
            self.teleport_timer += dt
            if self.teleport_timer >= 30.0:  # 30 seconds
                self.teleport_to_random_tile(walkable_tiles)
                self.teleport_timer = 0
