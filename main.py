import pygame
import sys

pygame.init()

# Основные настройки
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Инициализация экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Платформер с боссом")

# Игрок
player = pygame.Rect(50, HEIGHT - 70, 50, 50)
player_speed = 5
player_jump = 15
gravity = 0.8
player_velocity_y = 0
jumping = False

# Платформы для каждого уровня
levels = [
    [  # Уровень 1
        pygame.Rect(50, HEIGHT - 50, 100, 20),
        pygame.Rect(200, HEIGHT - 150, 100, 20),
        pygame.Rect(400, HEIGHT - 250, 100, 20),
        pygame.Rect(600, HEIGHT - 350, 100, 20),
    ],
    [  # Уровень 2
        pygame.Rect(50, HEIGHT - 50, 100, 20),
        pygame.Rect(150, HEIGHT - 100, 100, 20),
        pygame.Rect(300, HEIGHT - 200, 100, 20),
        pygame.Rect(500, HEIGHT - 300, 100, 20),
        pygame.Rect(700, HEIGHT - 400, 100, 20),
    ],
    [  # Уровень 3
        pygame.Rect(50, HEIGHT - 50, 100, 20),
        pygame.Rect(100, HEIGHT - 100, 100, 20),
        pygame.Rect(250, HEIGHT - 200, 100, 20),
        pygame.Rect(400, HEIGHT - 300, 100, 20),
        pygame.Rect(600, HEIGHT - 400, 100, 20),
    ],
    [  # Уровень 4 (Усложненный)
        pygame.Rect(50, HEIGHT - 50, 100, 20),
        pygame.Rect(200, HEIGHT - 150, 100, 20),
        pygame.Rect(350, HEIGHT - 250, 100, 20),
        pygame.Rect(500, HEIGHT - 350, 100, 20),
        pygame.Rect(650, HEIGHT - 450, 100, 20),
    ],
    [  # Уровень 5 (Босс)
        pygame.Rect(50, HEIGHT - 50, 100, 20),
        pygame.Rect(200, HEIGHT - 150, 100, 20),
        pygame.Rect(400, HEIGHT - 250, 100, 20),
        pygame.Rect(600, HEIGHT - 350, 100, 20),
        pygame.Rect(700, HEIGHT - 400, 100, 20),
    ]
]



# Враг (Босс)
boss = pygame.Rect(WIDTH - 150, HEIGHT - 70, 50, 50)

# Переменные уровня
level = 0
max_level = len(levels)

def draw_platforms():
    for platform in levels[level]:
        pygame.draw.rect(screen, GREEN, platform)

def reset_level():
    global player, jumping, player_velocity_y, level
    player.x, player.y = 50, HEIGHT - 70
    jumping = False
    player_velocity_y = 0
    level = 0  # Возвращение на первый уровень

def check_collisions():
    global jumping, player_velocity_y
    for platform in levels[level]:
        if player.colliderect(platform):
            if player_velocity_y > 0:  # Падение
                player.bottom = platform.top
                player_velocity_y = 0
                jumping = False
            elif player_velocity_y < 0:  # Прыжок
                player.top = platform.bottom
                player_velocity_y = 0

    if player.colliderect(boss) and level == max_level - 1:
        print("Вы победили босса!")
        pygame.quit()
        sys.exit()

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

    # Предотвращение выхода за границы окна
    if player.left < 0:
        player.left = 0
    if player.right > WIDTH:
        player.right = WIDTH

    # Применение гравитации
    player_velocity_y += gravity
    player.y += player_velocity_y

    check_collisions()

    # Проверка падения в пропасть
    if player.bottom > HEIGHT:
        print("Вы упали в пропасть!")
        reset_level()

    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, player)
    draw_platforms()

    if level == max_level - 1:
        pygame.draw.rect(screen, RED, boss)

    pygame.display.flip()
    clock.tick(FPS)

    if player.right >= WIDTH and level < max_level - 1:
        level += 1
        reset_level()
