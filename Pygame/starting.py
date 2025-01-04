import pygame
import random
import sys
import subprocess  # Import subprocess for running external scripts

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
WHITE = (255, 255, 255)

# Fonts
font = pygame.font.Font(pygame.font.match_font('courier'), 50)  # Monospace font
small_font = pygame.font.Font(pygame.font.match_font('courier'), 32)

# Menu options
menu_options = ["Play", "Save Game", "Credits"]
selected_option = 0  # Tracks the currently selected menu option

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

# Draw title and menu
def draw_menu(selected_option):
    # Title
    title = font.render("ENVIRON CTR", True, BLUE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # Menu options
    for i, option in enumerate(menu_options):
        color = BLUE if i == selected_option else WHITE
        text = small_font.render(option, True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 50))

# Draw footer
def draw_footer():
    footer_text_1 = small_font.render("24556  DR 5", True, BLUE)
    screen.blit(footer_text_1, (20, HEIGHT - 40))
    footer_text_2 = small_font.render("95654595  82008599", True, BLUE)
    screen.blit(footer_text_2, (WIDTH - 300, HEIGHT - 40))

# Game pages
def play_game():
    try:
        subprocess.run(["python3", "main.py"])  # Use 'python3' or 'python' based on your environment
        # Quit the current Pygame window before running the external script
        pygame.quit()
        sys.exit()  # Ensure the current program exits completely
    except FileNotFoundError:
        # Handle case where the script is not found
        print("Error: AI.py not found!")
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))

def save_game():
    screen.fill(DARK_BLUE)
    text = font.render("Game Saved!", True, BLUE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))

def credits_page():
    screen.fill(DARK_BLUE)
    text = font.render("Credits", True, BLUE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
    details = small_font.render("Designed by: Oscar Kuo, Benson Chen", True, WHITE)
    screen.blit(details, (WIDTH // 2 - details.get_width() // 2, HEIGHT // 2 + 50))

# Main loop
clock = pygame.time.Clock()
grid_data = generate_grid_data()
update_timer = 0
current_page = "menu"  # Tracks the current page: "menu", "play", "save", "credits"

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if current_page == "menu":
            # Menu navigation
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:  # Move up
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_s:  # Move down
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:  # Select option
                    if menu_options[selected_option] == "Play":
                        play_game()  # Call the external game script
                    elif menu_options[selected_option] == "Save Game":
                        current_page = "save"
                    elif menu_options[selected_option] == "Credits":
                        current_page = "credits"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Return to menu from any page
            current_page = "menu"

    # Clear the screen
    screen.fill(DARK_BLUE)

    # Update grid data periodically
    update_timer += clock.get_time()
    if update_timer > 500:  # Update every 500ms
        grid_data = generate_grid_data()
        update_timer = 0

    # Render the current page
    if current_page == "menu":
        draw_grid(grid_data)
        draw_menu(selected_option)
        draw_footer()
    elif current_page == "save":
        save_game()
    elif current_page == "credits":
        credits_page()

    # Update the display
    pygame.display.flip()
    clock.tick(30)
