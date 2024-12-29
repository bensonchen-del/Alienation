import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Futuristic Display")

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 255, 255)
DARK_BLUE = (0, 50, 50)
GRID_COLOR = (0, 80, 80)

# Fonts
font = pygame.font.Font(pygame.font.match_font('courier'), 50)  # Monospace font
small_font = pygame.font.Font(pygame.font.match_font('courier'), 32)

# Grid settings
GRID_SIZE = 20  # Size of each grid cell
GRID_ROWS = HEIGHT // GRID_SIZE
GRID_COLS = WIDTH // GRID_SIZE

# Generate random numbers for the grid
def generate_grid_data():
    return [[random.choice([" ", "•", random.randint(0, 9)]) for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

# Draw grid with data
def draw_grid(grid_data):
    for y, row in enumerate(grid_data):
        for x, cell in enumerate(row):
            if cell == "•":
                # Draw dot
                pygame.draw.circle(screen, GRID_COLOR, (x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2), 2)
            elif isinstance(cell, int):
                # Draw numbers
                text = small_font.render(str(cell), True, GRID_COLOR)
                screen.blit(text, (x * GRID_SIZE + 5, y * GRID_SIZE + 5))

# Draw title and details
def draw_text():
    # Title
    title = font.render("ENVIRON CTR", True, BLUE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
    
    # Footer
    footer_text_1 = small_font.render("24556  DR 5", True, BLUE)
    screen.blit(footer_text_1, (20, HEIGHT - 40))
    footer_text_2 = small_font.render("95654595  82008599", True, BLUE)
    screen.blit(footer_text_2, (WIDTH - 300, HEIGHT - 40))

# Main loop
clock = pygame.time.Clock()
grid_data = generate_grid_data()
update_timer = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Clear the screen
    screen.fill(DARK_BLUE)

    # Update grid data periodically
    update_timer += clock.get_time()
    if update_timer > 500:  # Update every 500ms
        grid_data = generate_grid_data()
        update_timer = 0

    # Draw grid and text
    draw_grid(grid_data)
    draw_text()

    # Update the display
    pygame.display.flip()
    clock.tick(30)