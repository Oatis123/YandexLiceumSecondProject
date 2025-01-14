import pygame
import sys
import random

pygame.init()

# Основные настройки
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FONT = pygame.font.Font(None, 74)

# Инициализация экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Процедурный Платформер с Боссом")

# Игрок
player = pygame.Rect(50, HEIGHT - 70, 50, 50)
player_speed = 5
player_jump = 15
gravity = 0.8
player_velocity_y = 0
jumping = False

# Переменные уровня
levels = []
level = 0
num_levels = 5

def generate_level():
    level = []
    platform_width = random.randint(80, 150)
    x = 50
    y = HEIGHT - 50
    level.append(pygame.Rect(x, y, platform_width, 20))

    for _ in range(random.randint(5, 10)):
        x += random.randint(100, 200)
        y_change = random.choice([-1, 1]) * random.randint(30, 100)
        y = max(min(y + y_change, HEIGHT - 50), 50)

        platform_type = random.choice(["normal", "moving", "disappearing"])
        platform_width = random.randint(80, 150)

        if platform_type == "normal":
            level.append(pygame.Rect(x, y, platform_width, 20))
        elif platform_type == "moving":
            level.append({"rect": pygame.Rect(x, y, platform_width, 20), "type": "moving", "direction": 1})
        elif platform_type == "disappearing":
            level.append({"rect": pygame.Rect(x, y, platform_width, 20), "type": "disappearing", "timer": random.randint(60, 120)})

    # Добавление платформы, ведущей к финишу
    finish_x = WIDTH - random.randint(100, 150)
    finish_y = random.randint(50, HEIGHT - 150)
    level.append(pygame.Rect(finish_x, finish_y, 100, 20))

    return level

def draw_platforms():
    for platform in levels[level]:
        if isinstance(platform, dict):
            if platform["type"] == "moving":
                platform["rect"].x += platform["direction"] * 2
                if platform["rect"].left <= 0 or platform["rect"].right >= WIDTH:
                    platform["direction"] *= -1
            elif platform["type"] == "disappearing":
                platform["timer"] -= 1
                if platform["timer"] <= 0:
                    continue
        pygame.draw.rect(screen, GREEN, platform["rect"] if isinstance(platform, dict) else platform)

def reset_level():
    global player, jumping, player_velocity_y
    player.x, player.y = 50, HEIGHT - 70
    jumping = False
    player_velocity_y = 0

def check_collisions():
    global jumping, player_velocity_y
    for platform in levels[level]:
        rect = platform["rect"] if isinstance(platform, dict) else platform
        if player.colliderect(rect):
            if player_velocity_y > 0:  # Падение
                player.bottom = rect.top
                player_velocity_y = 0
                jumping = False
            elif player_velocity_y < 0:  # Прыжок
                player.top = rect.bottom
                player_velocity_y = 0

def show_menu():
    global num_levels
    menu = True
    while menu:
        screen.fill(WHITE)
        text = FONT.render("Выберите количество уровней", True, BLUE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
        for i in range(1, 6):
            option = FONT.render(str(i), True, RED)
            screen.blit(option, (WIDTH // 2 - 20, HEIGHT // 2 - 100 + i * 60))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in range(pygame.K_1, pygame.K_6):
                    num_levels = event.key - pygame.K_0
                    menu = False

show_menu()

# Генерация уровней
for _ in range(num_levels):
    levels.append(generate_level())

clock = pygame.time.Clock()

# Игровой цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.x += player_speed
    if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and not jumping:
        jumping = True
        player_velocity_y = -player_jump

    if player.left < 0:
        player.left = 0
    if player.right > WIDTH:
        player.right = WIDTH
        if level < num_levels - 1:
            level += 1
            reset_level()

    player_velocity_y += gravity
    player.y += player_velocity_y

    check_collisions()

    if player.bottom > HEIGHT:
        print("Вы упали в пропасть!")
        reset_level()

    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, player)
    draw_platforms()

    pygame.display.flip()
    clock.tick(FPS)
