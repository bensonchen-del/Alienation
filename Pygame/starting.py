import pygame
import random
import sys
import subprocess  # Import subprocess for running external scripts

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Load and play background music
mp3_file = "Alien Soundtrack Track 6 The Passage Jerry Goldsmith.mp3"
try:
    pygame.mixer.music.load(mp3_file)
    pygame.mixer.music.play(-1)  # -1 means loop indefinitely
except pygame.error as e:
    print(f"Unable to load MP3 file: {e}")
    sys.exit()

# Screen settings
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Futuristic Display")

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 200, 200)
DARK_BLUE = (0, 30, 30)
GRID_COLOR = (0, 50, 50)
WHITE = (255, 255, 255)

# Fonts
font = pygame.font.Font(pygame.font.match_font('courier'), 50)  # Monospace font
small_font = pygame.font.Font(pygame.font.match_font('courier'), 32)

# Menu options
menu_options = ["Play", "Credits"]
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
        pygame.quit()  # 在啟動 main.py 之前關閉 Pygame 視窗
        subprocess.run([sys.executable, "main.py"])  # 使用 sys.executable 啟動 main.py
        sys.exit()  # 確保退出 starting.py
    except FileNotFoundError:
        # 處理找不到 main.py 的情況
        pygame.init()  # 重新初始化 Pygame 以顯示錯誤訊息
        screen.fill(DARK_BLUE)
        error_message = small_font.render("Error: main.py not found!", True, BLUE)
        screen.blit(error_message, (WIDTH // 2 - error_message.get_width() // 2, HEIGHT // 2 - 50))
        pygame.display.flip()
        pygame.time.wait(3000)  # 顯示 3 秒後退出
        pygame.quit()
        sys.exit()

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
current_page = "menu"  # Tracks the current page: "menu", "play", "credits"

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()  # Stop the music when quitting
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
    elif current_page == "credits":
        credits_page()

    # Update the display
    pygame.display.flip()
    clock.tick(30)
