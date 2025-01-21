import pygame
import sys
import random
import sqlite3
from math import sin, cos, radians

pygame.init()

# Конфигурация игры
WIDTH, HEIGHT = 1000, 800
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

FONT = pygame.font.Font(None, 74)
SMALL_FONT = pygame.font.Font(None, 36)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Платформер с Боссом")

# База данных
conn = sqlite3.connect('game.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY, 
                 username TEXT UNIQUE, 
                 password TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                (id INTEGER PRIMARY KEY,
                 user_id INTEGER,
                 score INTEGER,
                 FOREIGN KEY(user_id) REFERENCES users(id))''')
conn.commit()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(50, HEIGHT-150))
        self.speed = 7
        self.jump_power = -16
        self.gravity = 0.8
        self.velocity_y = 0
        self.on_ground = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="normal"):
        super().__init__()
        self.platform_type = platform_type
        self.colors = {
            "normal": GREEN,
            "spike": RED,
            "moving": ORANGE,
            "disappearing": GRAY
        }
        self.image = pygame.Surface((width, height))
        self.image.fill(self.colors[platform_type])
        self.rect = self.image.get_rect(topleft=(x, y))
        
        if platform_type == "spike":
            self._add_spikes()
        
        self.direction = 1 if random.random() < 0.5 else -1
        self.speed = 2
        self.disappear_timer = 0
        self.should_disappear = False

    def _add_spikes(self):
        spike_width = 10
        for i in range(0, self.rect.width, spike_width*2):
            points = [
                (i, self.rect.height),
                (i + spike_width, self.rect.height),
                (i + spike_width//2, 0)
            ]
            pygame.draw.polygon(self.image, BLACK, points)

    def update(self):
        if self.platform_type == "moving":
            self.rect.x += self.direction * self.speed
            if self.rect.left < 0 or self.rect.right > WIDTH:
                self.direction *= -1
        
        if self.platform_type == "disappearing" and self.should_disappear:
            self.disappear_timer += 1
            if self.disappear_timer >= 60:  # 1 секунда
                self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((120, 180))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topright=(WIDTH-50, 100))
        self.health = 20
        self.angle = 0
        self.projectiles = pygame.sprite.Group()
        self.shoot_timer = 0

    def update(self):
        self.angle += 3
        self.rect.y = 200 + sin(radians(self.angle)) * 150
        self.shoot_timer += 1
        
        if self.shoot_timer >= 60:
            self.shoot()
            self.shoot_timer = 0
            
        self.projectiles.update()

    def shoot(self):
        projectile = Projectile(self.rect.centerx, self.rect.centery, 180)
        self.projectiles.add(projectile)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 8
        self.angle = radians(angle)

    def update(self):
        self.rect.x += cos(self.angle) * self.speed
        self.rect.y += sin(self.angle) * self.speed
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def login_menu():
    username = ""
    password = ""
    active = "username"
    error = ""

    while True:
        screen.fill(WHITE)
        draw_text("Вход/Регистрация", FONT, BLUE, WIDTH//2, 100)
        
        # Поле логина
        pygame.draw.rect(screen, BLUE, (WIDTH//2-150, 200, 300, 50), 2)
        draw_text(username if username else "Логин", SMALL_FONT, BLUE, WIDTH//2, 225)
        
        # Поле пароля
        pygame.draw.rect(screen, BLUE, (WIDTH//2-150, 300, 300, 50), 2)
        draw_text("*"*len(password) if password else "Пароль", SMALL_FONT, BLUE, WIDTH//2, 325)
        
        # Сообщение об ошибке
        if error:
            draw_text(error, SMALL_FONT, RED, WIDTH//2, 400)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username and password:
                        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
                        user = cursor.fetchone()
                        if user:
                            if user[2] == password:
                                return username
                            else:
                                error = "Неверный пароль!"
                        else:
                            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                                        (username, password))
                            conn.commit()
                            return username
                elif event.key == pygame.K_TAB:
                    active = "password" if active == "username" else "username"
                elif event.key == pygame.K_BACKSPACE:
                    if active == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                else:
                    if event.unicode.isalnum():
                        if active == "username":
                            username += event.unicode
                        else:
                            password += event.unicode

def level_select():
    selected = ""
    while True:
        screen.fill(WHITE)
        draw_text("Выберите количество уровней (1-100)", SMALL_FONT, BLUE, WIDTH//2, 100)
        pygame.draw.rect(screen, BLUE, (WIDTH//2-100, 150, 200, 50), 2)
        draw_text(selected if selected else "Введите число", SMALL_FONT, BLUE, WIDTH//2, 175)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if selected.isdigit() and 1 <= int(selected) <= 100:
                        return int(selected)
                elif event.key == pygame.K_BACKSPACE:
                    selected = selected[:-1]
                elif event.unicode.isdigit():
                    selected += event.unicode

def game_loop(total_levels, username):
    player = Player()
    boss = Boss()
    platforms = pygame.sprite.Group()
    dangerous_platforms = pygame.sprite.Group()
    
    current_level = 1
    score = 0

    def generate_level():
        platforms.empty()
        dangerous_platforms.empty()
        
        if current_level <= total_levels:
            x = 100
            y = HEIGHT - 100
            prev_y = y
            
            platforms.add(Platform(x-50, HEIGHT-50, 200, 50))
            
            for _ in range(random.randint(10, 15)):
                x += random.randint(120, 200)
                y_change = random.choice([-1, 1]) * random.randint(50, 150)
                y = prev_y + y_change
                y = max(200, min(y, HEIGHT - 100))
                
                platform_type = "normal"
                rand_val = random.random()
                if rand_val < 0.15:
                    platform_type = "spike"
                elif rand_val < 0.3:
                    platform_type = "moving"
                elif rand_val < 0.45:
                    platform_type = "disappearing"
                
                platform = Platform(x, y, random.randint(80, 150), 30, platform_type)
                
                if platform_type == "spike":
                    dangerous_platforms.add(platform)
                else:
                    platforms.add(platform)
                
                prev_y = y
            
            platforms.add(Platform(WIDTH-200, 200, 200, 50))
        else:
            platforms.add(Platform(0, HEIGHT-30, WIDTH, 50))
            platforms.add(Platform(WIDTH//2-200, HEIGHT//2+150, 400, 30))
            platforms.add(Platform(100, HEIGHT//2, 200, 30))
            platforms.add(Platform(WIDTH-300, HEIGHT//2, 200, 30))

    def reset_level():
        nonlocal player
        player = Player()
        generate_level()

    generate_level()

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_a]:
            player.rect.x -= player.speed
        if keys[pygame.K_d]:
            player.rect.x += player.speed
        if keys[pygame.K_SPACE] and player.on_ground:
            player.velocity_y = player.jump_power
            player.on_ground = False

        player.velocity_y += player.gravity
        player.rect.y += player.velocity_y

        if player.rect.y > HEIGHT + 100:
            reset_level()

        platforms.update()

        hit_platforms = pygame.sprite.spritecollide(player, platforms, False)
        on_platform = False
        
        for platform in hit_platforms:
            if platform.platform_type == "disappearing":
                platform.should_disappear = True
            
            if player.velocity_y > 0:
                if platform.rect.top < player.rect.bottom:
                    player.rect.bottom = platform.rect.top
                    player.velocity_y = 0
                    player.on_ground = True
                    on_platform = True

        if pygame.sprite.spritecollide(player, dangerous_platforms, False):
            reset_level()

        if player.rect.x > WIDTH:
            current_level += 1
            score += 10
            if current_level > total_levels + 1:
                cursor.execute("INSERT INTO scores (user_id, score) VALUES ((SELECT id FROM users WHERE username=?), ?)",
                            (username, score))
                conn.commit()
                return score
            generate_level()
            player.rect.topleft = (50, HEIGHT-150)

        boss_phase = current_level > total_levels
        if boss_phase:
            boss.update()
            if pygame.sprite.spritecollide(player, boss.projectiles, True):
                reset_level()
            
            if pygame.sprite.collide_rect(player, boss):
                boss.health -= 1
                if boss.health <= 0:
                    score += 100
                    cursor.execute("INSERT INTO scores (user_id, score) VALUES ((SELECT id FROM users WHERE username=?), ?)",
                                (username, score))
                    conn.commit()
                    return score

        screen.fill(WHITE)
        platforms.draw(screen)
        dangerous_platforms.draw(screen)
        screen.blit(player.image, player.rect)
        
        draw_text(f"Уровень: {current_level}/{total_levels}", SMALL_FONT, BLUE, 100, 20)
        draw_text(f"Очки: {score}", SMALL_FONT, BLUE, 100, 60)
        
        if boss_phase:
            screen.blit(boss.image, boss.rect)
            boss.projectiles.draw(screen)
            pygame.draw.rect(screen, RED, (WIDTH-220, 20, 200, 30))
            pygame.draw.rect(screen, GREEN, (WIDTH-220, 20, boss.health*10, 30))
        
        pygame.display.flip()
        clock.tick(FPS)

def final_screen(score):
    while True:
        screen.fill(WHITE)
        draw_text(f"Игра окончена! Счет: {score}", FONT, BLUE, WIDTH//2, HEIGHT//2 - 50)
        draw_text("M - В меню", SMALL_FONT, BLUE, WIDTH//2, HEIGHT//2 + 50)
        draw_text("Q - Выход", SMALL_FONT, BLUE, WIDTH//2, HEIGHT//2 + 100)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    return True
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main():
    while True:
        username = login_menu()
        total_levels = level_select()
        while True:
            score = game_loop(total_levels, username)
            if not final_screen(score):
                break

if __name__ == "__main__":
    main()
    conn.close()