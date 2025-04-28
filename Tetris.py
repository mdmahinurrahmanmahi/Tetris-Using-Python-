import pygame
import random
import time

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GRAY = (50, 50, 50)

# Game constants
BASE_BLOCK_SIZE = 40  # Base size for reference
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH_RATIO = 0.36  # Sidebar takes 35% of the width
MIN_WIDTH = 600  # Minimum window width
MIN_HEIGHT = 800  # Minimum window height

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]  # Z
]

# Colors for each shape
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# Load font
try:
    title_font = pygame.font.Font(None, 72)
    large_font = pygame.font.Font(None, 48)
    medium_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
except:
    # Fallback if font loading fails
    title_font = pygame.font.SysFont('arial', 72)
    large_font = pygame.font.SysFont('arial', 48)
    medium_font = pygame.font.SysFont('arial', 36)
    small_font = pygame.font.SysFont('arial', 24)

clock = pygame.time.Clock()


class Tetromino:
    def __init__(self):
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color = SHAPE_COLORS[self.shape_idx]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        # Transpose the shape matrix and reverse each row to rotate 90 degrees clockwise
        rotated = [[self.shape[y][x] for y in range(len(self.shape) - 1, -1, -1)]
                   for x in range(len(self.shape[0]))]
        return rotated


def calculate_sizes(screen_width, screen_height):
    # Calculate block size based on height (maintain aspect ratio)
    block_size = max(20, min(screen_height // GRID_HEIGHT,
                             (screen_width * (1 - SIDEBAR_WIDTH_RATIO)) // GRID_WIDTH))

    # Recalculate sidebar width based on actual block size
    game_area_width = block_size * GRID_WIDTH
    sidebar_width = screen_width - game_area_width

    return block_size, game_area_width, sidebar_width


def draw_grid(screen, grid, block_size, game_area_width):
    # Draw game area background
    pygame.draw.rect(screen, DARK_GRAY,
                     (0, 0,
                      game_area_width,
                      block_size * GRID_HEIGHT))

    # Draw grid lines
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, GRAY,
                         (x * block_size, 0),
                         (x * block_size, block_size * GRID_HEIGHT))
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, GRAY,
                         (0, y * block_size),
                         (game_area_width, y * block_size))

    # Draw blocks
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x]:
                pygame.draw.rect(screen, SHAPE_COLORS[grid[y][x] - 1],
                                 (x * block_size + 1,
                                  y * block_size + 1,
                                  block_size - 2, block_size - 2))
                # Add highlight effect
                highlight = pygame.Surface((block_size - 2, block_size - 2), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 50))
                screen.blit(highlight, (x * block_size + 1,
                                        y * block_size + 1))


def draw_tetromino(screen, tetromino, block_size, game_area_width):
    for y in range(len(tetromino.shape)):
        for x in range(len(tetromino.shape[0])):
            if tetromino.shape[y][x]:
                pygame.draw.rect(screen, tetromino.color,
                                 ((tetromino.x + x) * block_size + 1,
                                  (tetromino.y + y) * block_size + 1,
                                  block_size - 2, block_size - 2))
                # Add highlight effect
                highlight = pygame.Surface((block_size - 2, block_size - 2), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 50))
                screen.blit(highlight, ((tetromino.x + x) * block_size + 1,
                                        (tetromino.y + y) * block_size + 1))


def check_collision(grid, tetromino, offset_x=0, offset_y=0):
    for y in range(len(tetromino.shape)):
        for x in range(len(tetromino.shape[0])):
            if tetromino.shape[y][x]:
                new_x = tetromino.x + x + offset_x
                new_y = tetromino.y + y + offset_y
                if (new_x < 0 or new_x >= GRID_WIDTH or
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and grid[new_y][new_x])):
                    return True
    return False


def merge_tetromino(grid, tetromino):
    for y in range(len(tetromino.shape)):
        for x in range(len(tetromino.shape[0])):
            if tetromino.shape[y][x]:
                grid[tetromino.y + y][tetromino.x + x] = tetromino.shape_idx + 1


def clear_lines(grid):
    lines_cleared = 0
    for y in range(GRID_HEIGHT):
        if all(grid[y]):
            lines_cleared += 1
            for y2 in range(y, 0, -1):
                grid[y2] = grid[y2 - 1][:]
            grid[0] = [0] * GRID_WIDTH
    return lines_cleared


def draw_text(screen, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)


def draw_centered_text(screen, text, font, color, y, screen_width):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(screen_width // 2, y))
    screen.blit(text_surface, text_rect)


def draw_game_over(screen, score, screen_width, screen_height):
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    draw_centered_text(screen, "GAME OVER", title_font, WHITE, screen_height // 2 - 60, screen_width)
    draw_centered_text(screen, f"Score: {score}", large_font, WHITE, screen_height // 2, screen_width)
    draw_centered_text(screen, "Press Enter to Restart", medium_font, WHITE, screen_height // 2 + 50, screen_width)
    draw_centered_text(screen, "Press Q to Quit", medium_font, WHITE, screen_height // 2 + 120, screen_width)


def draw_start_menu(screen, screen_width, screen_height):
    screen.fill(BLACK)

    # Title
    draw_centered_text(screen, "TETRIS", title_font, WHITE, screen_height // 4, screen_width)

    # Start button
    button_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2 - 40, 300, 80)
    pygame.draw.rect(screen, GREEN, button_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, button_rect, 3, border_radius=10)
    draw_centered_text(screen, "START", large_font, BLACK, screen_height // 2, screen_width)

    # Instructions
    draw_centered_text(screen, "Controls:", medium_font, WHITE, screen_height * 3 // 4 - 60, screen_width)
    draw_centered_text(screen, "Arrow Keys: Move", small_font, WHITE, screen_height * 3 // 4 - 20, screen_width)
    draw_centered_text(screen, "Up Arrow: Rotate", small_font, WHITE, screen_height * 3 // 4 + 10, screen_width)
    draw_centered_text(screen, "Space: Hard Drop", small_font, WHITE, screen_height * 3 // 4 + 40, screen_width)
    draw_centered_text(screen, "Press Q to Quit", small_font, WHITE, screen_height * 3 // 4 + 80, screen_width)


def draw_game_ui(screen, score, level, lines, next_tetromino, block_size, game_area_width, sidebar_width,
                 screen_height):
    # Sidebar background
    sidebar_rect = pygame.Rect(game_area_width, 0, sidebar_width, screen_height)
    pygame.draw.rect(screen, DARK_GRAY, sidebar_rect)

    # Calculate scaling factor for UI elements
    ui_scale = block_size / BASE_BLOCK_SIZE

    # Draw game info
    info_x = game_area_width + 20 * ui_scale

    draw_text(screen, "SCORE", medium_font, WHITE, info_x, 40 * ui_scale)
    pygame.draw.rect(screen, WHITE, (info_x - 10 * ui_scale, 80 * ui_scale,
                                     sidebar_width - 40 * ui_scale, 60 * ui_scale), 2)
    draw_text(screen, f"{score:08d}", large_font, WHITE, info_x + 10 * ui_scale, 100 * ui_scale)

    draw_text(screen, "LEVEL", medium_font, WHITE, info_x, 180 * ui_scale)
    pygame.draw.rect(screen, WHITE, (info_x - 10 * ui_scale, 220 * ui_scale,
                                     sidebar_width - 40 * ui_scale, 60 * ui_scale), 2)
    draw_text(screen, f"{level:02d}", large_font, WHITE, info_x + 10 * ui_scale, 240 * ui_scale)

    draw_text(screen, "LINES", medium_font, WHITE, info_x, 320 * ui_scale)
    pygame.draw.rect(screen, WHITE, (info_x - 10 * ui_scale, 360 * ui_scale,
                                     sidebar_width - 40 * ui_scale, 60 * ui_scale), 2)
    draw_text(screen, f"{lines:04d}", large_font, WHITE, info_x + 10 * ui_scale, 380 * ui_scale)

    # Next piece
    draw_text(screen, "NEXT", medium_font, WHITE, info_x, 460 * ui_scale)
    next_piece_rect = pygame.Rect(info_x - 10 * ui_scale, 500 * ui_scale,
                                  sidebar_width - 40 * ui_scale, 160 * ui_scale)
    pygame.draw.rect(screen, WHITE, next_piece_rect, 2)

    # Draw next tetromino centered in its area
    next_width = len(next_tetromino.shape[0])
    next_height = len(next_tetromino.shape)
    next_block_size = min(
        (next_piece_rect.width - 20) // next_width,
        (next_piece_rect.height - 20) // next_height
    )

    start_x = next_piece_rect.centerx - (next_width * next_block_size) // 2
    start_y = next_piece_rect.centery - (next_height * next_block_size) // 2

    for y in range(next_height):
        for x in range(next_width):
            if next_tetromino.shape[y][x]:
                pygame.draw.rect(screen, next_tetromino.color,
                                 (start_x + x * next_block_size + 1,
                                  start_y + y * next_block_size + 1,
                                  next_block_size - 2, next_block_size - 2))
                highlight = pygame.Surface((next_block_size - 2, next_block_size - 2), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 50))
                screen.blit(highlight, (start_x + x * next_block_size + 1,
                                        start_y + y * next_block_size + 1))


def main():
    # Initialize screen at the beginning of main()
    initial_width = BASE_BLOCK_SIZE * GRID_WIDTH * (1 + SIDEBAR_WIDTH_RATIO)
    initial_height = BASE_BLOCK_SIZE * GRID_HEIGHT
    screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
    pygame.display.set_caption("Tetris")

    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    current_tetromino = Tetromino()
    next_tetromino = Tetromino()
    score = 0
    level = 1
    lines = 0
    fall_time = 0
    fall_speed = 0.5  # seconds
    game_over = False
    in_menu = True

    running = True
    while running:
        current_width, current_height = screen.get_size()

        # Enforce minimum window size
        if current_width < MIN_WIDTH or current_height < MIN_HEIGHT:
            new_width = max(current_width, MIN_WIDTH)
            new_height = max(current_height, MIN_HEIGHT)
            screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            current_width, current_height = new_width, new_height

        # Calculate sizes based on current window dimensions
        block_size, game_area_width, sidebar_width = calculate_sizes(current_width, current_height)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                new_width, new_height = event.size
                if new_width < MIN_WIDTH or new_height < MIN_HEIGHT:
                    new_width = max(new_width, MIN_WIDTH)
                    new_height = max(new_height, MIN_HEIGHT)
                screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                current_width, current_height = new_width, new_height
                block_size, game_area_width, sidebar_width = calculate_sizes(current_width, current_height)

            if in_menu:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    button_rect = pygame.Rect(current_width // 2 - 150, current_height // 2 - 40, 300, 80)
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        in_menu = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        in_menu = False
                    elif event.key == pygame.K_q:
                        running = False
            elif game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Reset game
                        grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                        current_tetromino = Tetromino()
                        next_tetromino = Tetromino()
                        score = 0
                        level = 1
                        lines = 0
                        fall_speed = 0.5
                        game_over = False
                    elif event.key == pygame.K_q:
                        running = False
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if not check_collision(grid, current_tetromino, -1, 0):
                            current_tetromino.x -= 1
                    elif event.key == pygame.K_RIGHT:
                        if not check_collision(grid, current_tetromino, 1, 0):
                            current_tetromino.x += 1
                    elif event.key == pygame.K_DOWN:
                        if not check_collision(grid, current_tetromino, 0, 1):
                            current_tetromino.y += 1
                    elif event.key == pygame.K_UP:
                        rotated_shape = current_tetromino.rotate()
                        old_shape = current_tetromino.shape
                        current_tetromino.shape = rotated_shape
                        if check_collision(grid, current_tetromino):
                            current_tetromino.shape = old_shape
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        while not check_collision(grid, current_tetromino, 0, 1):
                            current_tetromino.y += 1
                        merge_tetromino(grid, current_tetromino)
                        lines_cleared = clear_lines(grid)
                        lines += lines_cleared
                        score += lines_cleared * lines_cleared * 100 * level
                        level = score // 2000 + 1
                        fall_speed = max(0.05, 0.5 - (level - 1) * 0.05)
                        current_tetromino = next_tetromino
                        next_tetromino = Tetromino()
                        if check_collision(grid, current_tetromino):
                            game_over = True

        if in_menu:
            draw_start_menu(screen, current_width, current_height)
        elif game_over:
            screen.fill(BLACK)
            draw_grid(screen, grid, block_size, game_area_width)
            draw_game_ui(screen, score, level, lines, next_tetromino, block_size, game_area_width, sidebar_width,
                         current_height)
            draw_game_over(screen, score, current_width, current_height)
        else:
            # Game logic
            current_time = time.time()
            if current_time - fall_time > fall_speed:
                if not check_collision(grid, current_tetromino, 0, 1):
                    current_tetromino.y += 1
                    fall_time = current_time
                else:
                    merge_tetromino(grid, current_tetromino)
                    lines_cleared = clear_lines(grid)
                    lines += lines_cleared
                    score += lines_cleared * lines_cleared * 100 * level
                    level = score // 2000 + 1
                    fall_speed = max(0.05, 0.5 - (level - 1) * 0.05)
                    current_tetromino = next_tetromino
                    next_tetromino = Tetromino()
                    if check_collision(grid, current_tetromino):
                        game_over = True

            # Drawing
            screen.fill(BLACK)
            draw_grid(screen, grid, block_size, game_area_width)
            draw_tetromino(screen, current_tetromino, block_size, game_area_width)
            draw_game_ui(screen, score, level, lines, next_tetromino, block_size, game_area_width, sidebar_width,
                         current_height)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()