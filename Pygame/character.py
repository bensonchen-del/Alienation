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

# Define Alien class
class Alien(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = ALIEN_SPEED  # Constant speed
        self.target = (x, y)      # Initial target is its starting position

    def set_target(self, x, y):
        self.target = (x, y)

    def update_position(self, dt, walls):
        dx = self.target[0] - self.rect.centerx
        dy = self.target[1] - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance != 0:
            # Calculate normalized direction vector
            move_x = (dx / distance) * self.speed * dt
            move_y = (dy / distance) * self.speed * dt

            # Move horizontally
            self.rect.x += move_x
            collided_walls = pygame.sprite.spritecollide(self, walls, False)
            if collided_walls:
                if move_x > 0:  # Moving right
                    self.rect.right = collided_walls[0].rect.left
                elif move_x < 0:  # Moving left
                    self.rect.left = collided_walls[0].rect.right

            # Move vertically
            self.rect.y += move_y
            collided_walls = pygame.sprite.spritecollide(self, walls, False)
            if collided_walls:
                if move_y > 0:  # Moving down
                    self.rect.bottom = collided_walls[0].rect.top
                elif move_y < 0:  # Moving up
                    self.rect.top = collided_walls[0].rect.bottom

