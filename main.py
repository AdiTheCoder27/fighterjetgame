import random
import pygame

# Setup
pygame.init()
WIDTH, HEIGHT = 1000, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Fighter Jet Game")
clock = pygame.time.Clock()

# Load images
player_img = pygame.transform.scale(pygame.image.load("assets/player.png"), (60, 60))
player_img = pygame.transform.rotate(player_img, -90)
enemy_img = pygame.transform.scale(pygame.image.load("assets/enemy.png"), (60, 60))
enemy_img = pygame.transform.rotate(enemy_img, 90)
bullet_img = pygame.transform.scale(pygame.image.load("assets/bullet.png"), (20, 10))
missile_img = pygame.transform.scale(pygame.image.load("assets/missile.png"), (30, 15))

# Player jet class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(center=(100, HEIGHT // 2))
        self.speed = 5
        self.health = 100

    def update(self, keys):
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def shoot(self, group, missile=False):
        if missile:
            proj = Projectile(self.rect.right, self.rect.centery, 10, is_missile=True)
        else:
            proj = Projectile(self.rect.right, self.rect.centery, 15)
        group.add(proj)


# Enemy jet class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(center=(random.randint(WIDTH + 50, WIDTH + 200), random.randint(50, HEIGHT - 50)))
        self.speed = random.randint(2, 4)
        self.last_shot = pygame.time.get_ticks()

    def update(self, bullets_group):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()
        now = pygame.time.get_ticks()
        if now - self.last_shot > random.randint(1500, 2500):
            bullet = Projectile(self.rect.left, self.rect.centery, -7)
            bullets_group.add(bullet)
            self.last_shot = now


# Projectiles (bullets and missiles)
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, is_missile=False):
        super().__init__()
        self.image = missile_img if is_missile else bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.is_missile = is_missile

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()


# Sprite groups
player = Player()
player_group = pygame.sprite.GroupSingle(player)
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Game loop


def game_loop():
    run = True
    font = pygame.font.SysFont("Arial", 24)
    score = 0
    spawn_event = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_event, 1500)

    while run:
        clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == spawn_event:
                enemies.add(Enemy())
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot(player_bullets)
                elif event.key == pygame.K_m:
                    player.shoot(player_bullets, missile=True)

        player.update(keys)
        player_bullets.update()
        enemy_bullets.update()
        enemies.update(enemy_bullets)

        # Handle collisions
        for enemy in pygame.sprite.groupcollide(enemies, player_bullets, True, True):
            score += 1

        if pygame.sprite.spritecollide(player, enemy_bullets, True):
            player.health -= 5
            if player.health <= 0:
                return show_game_over(score)

        # Drawing
        win.fill((15, 20, 40))
        player_group.draw(win)
        player_bullets.draw(win)
        enemy_bullets.draw(win)
        enemies.draw(win)

        # UI
        health_text = font.render(f"Health: {player.health}", True, (255, 100, 100))
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        win.blit(health_text, (10, 10))
        win.blit(score_text, (10, 40))

        pygame.display.update()

    pygame.quit()


def show_game_over(score):
    font = pygame.font.SysFont("Arial", 48)
    small_font = pygame.font.SysFont("Arial", 24)
    run = True
    while run:
        win.fill((0, 0, 0))
        text = font.render("Game Over", True, (255, 0, 0))
        score_text = small_font.render(f"Final Score: {score}", True, (255, 255, 255))
        hint = small_font.render("Press ESC to quit", True, (180, 180, 180))
        win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))
        win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        win.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 40))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

    pygame.quit()


game_loop()
