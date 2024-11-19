import pygame
from pygame.locals import *
import math
# Initializing Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer module

# Setting up game window parameters
WIDTH, HEIGHT = 768, 768
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Space Shooter")

# Loading the provided sprites
player_sprite_path = "player-sprite.png"
enemy_sprite_paths = [
    "enemy1.png",
    "enemy2.png",
    "enemy3.png"
]
# Loading the sound effects
shoot_sound = pygame.mixer.Sound('shoot.wav')
explosion_sound = pygame.mixer.Sound('explosion.wav')
playerhit_sound = pygame.mixer.Sound('ufo_highpitch.wav')
intro_sound = pygame.mixer.Sound('mixkit-boss-fight-arcade-232.wav')
playerdeath_sound = pygame.mixer.Sound('mixkit-funny-system-break-down-2955.wav')


# Loading player sprite
player_img = pygame.image.load(player_sprite_path)
if player_img is None:
    print("Error loading player sprite")
else:
    player_img = pygame.transform.scale(player_img, (50, 50))
    print("Player sprite loaded successfully")

# Loading enemy sprites
enemy_imgs = [pygame.image.load(path) for path in enemy_sprite_paths]
enemy_imgs = [pygame.transform.scale(img, (50, 50)) for img in enemy_imgs]

# Load Bullet sprite
bullet_sprite_path = "bullet-sprite.png"
bullet_img = pygame.image.load(bullet_sprite_path)
if bullet_img is None:
    print("Error loading bullet sprite")
else:
    bullet_img = pygame.transform.scale(bullet_img, (30, 30))
    print("Bullet sprite loaded successfully")

# Load Background image
background_img_path = "galaxy-background.JPG"
background_img = pygame.image.load(background_img_path)
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))


# Game Over screen
def game_over_screen():
    font = pygame.font.SysFont(None, 55)
    button_font = pygame.font.SysFont(None, 40)
    game_over_text = font.render('GAME OVER', True, (255, 0, 0))
    restart_button_text = button_font.render('Restart', True, (0, 0, 0))
    exit_button_text = button_font.render('Exit', True, (0, 0, 0))
    playerdeath_sound.play()
    while True:
        win.fill((0, 0, 0))
        win.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))
        restart_button = pygame.draw.rect(win, (0, 255, 0), (WIDTH // 3, HEIGHT // 2, 100, 50))
        exit_button = pygame.draw.rect(win, (255, 0, 0), (2 * WIDTH // 3 - 100, HEIGHT // 2, 100, 50))
        win.blit(restart_button_text, (WIDTH // 3 + 10, HEIGHT // 2 + 10))
        win.blit(exit_button_text, (2 * WIDTH // 3 - 90, HEIGHT // 2 + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if restart_button.collidepoint(x, y):
                    return True  # Restart the game
                if exit_button.collidepoint(x, y):
                    pygame.quit()  # Exit the game
                    exit()

        pygame.display.update()


# Player class
class Player:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.bullets = []
        self.health = 5

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(win)
        # Drawing health bar
        pygame.draw.rect(win, (255, 0, 0), (self.x, self.y - 20, 50, 10))
        pygame.draw.rect(win, (0, 255, 0), (self.x, self.y - 20, 50 * (self.health / 5), 10))

    def move_bullets(self):
        for bullet in self.bullets:
            bullet.move()
            if bullet.y < 0:
                self.bullets.remove(bullet)


# Bullet class
class Bullet:
    def __init__(self, x, y, x_speed=0, y_speed=-10, img=None, direction=1):
        self.x = x
        self.y = y
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.img = img
        self.direction = direction  # Add direction attribute
        self.speed = 10

    def draw(self, win):
        if self.img:
            win.blit(self.img, (self.x, self.y))
        else:
            pygame.draw.rect(win, (255, 255, 255), (self.x, self.y, 5, 10))  # Draw a rectangle for enemy bullets

    def move(self):
        self.y -= self.speed * self.direction  # Use direction attribute to determine movement direction


# Enemy class
class Enemy:
    def __init__(self, x, y, img, enemy_type=1, is_boss=False):
        self.is_boss = is_boss
        self.x = x
        self.y = y
        self.img = img
        self.enemy_type = enemy_type
        self.move_direction = 1
        self.is_boss = is_boss
        self.health = 50 if is_boss else 1
        self.elliptical_t = 0  # time parameter for elliptical motion

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def move(self):
        if self.is_boss:  # New condition for boss movement
            # Vertical elliptical pattern (modify these values as you see fit)
            self.x = WIDTH // 2 + 100 * math.cos(self.elliptical_t)
            self.y = HEIGHT // 4 + 50 * math.sin(self.elliptical_t)
            self.elliptical_t += 0.01  # Increment the time parameter
        elif self.enemy_type == 1:  # Horizontal movement
            self.x += self.move_direction * 5
            if self.x <= 0 or self.x >= WIDTH - 50:
                self.move_direction *= -1

        elif self.enemy_type == 2:  # Diagonal movement
            self.x += self.move_direction * 5
            self.y += self.move_direction * 3
            if self.x <= 0 or self.x >= WIDTH - 50 or self.y <= 0 or self.y >= HEIGHT - 50:
                self.move_direction *= -1

        elif self.enemy_type == 3:  # Sinusoidal movement
            self.x += self.move_direction * 5
            self.y = (HEIGHT // 4) + (HEIGHT // 4) * math.sin(self.x / 60)
            if self.x <= 0 or self.x >= WIDTH - 50:
                self.move_direction *= -1

    def fire_bullet(self, enemy_bullets):
        if self.is_boss:
            # Firing 4 bullets in a pattern
            enemy_bullets.append(Bullet(self.x, self.y + 50, direction=-1))
            enemy_bullets.append(Bullet(self.x + 20, self.y + 50, direction=-1))
            enemy_bullets.append(Bullet(self.x - 20, self.y + 50, direction=-1))
            enemy_bullets.append(Bullet(self.x + 40, self.y + 50, direction=-1))
        elif self.y < HEIGHT - 100 and len(enemy_bullets) < 10:
            enemy_bullets.append(
                Bullet(self.x + 22, self.y + 50, None, direction=-1))  # Direction set to -1, img set to None

    def fire_boss_bullet(self, enemy_bullets, angle):
        # Firing bullets at different angles
        x_component = 10 * math.cos(math.radians(angle))
        y_component = 10 * math.sin(math.radians(angle))
        enemy_bullets.append(Bullet(self.x + 22, self.y + 50, x_component, y_component))

    def move_boss(self):
        # Move the boss in a vertical elliptical pattern
        self.y += 3 * math.sin(self.x / 50)
        self.x += self.move_direction * 1  # Slower horizontal speed for the boss
        if self.x <= 0 or self.x >= WIDTH - 50:
            self.move_direction *= -1
# Checking collision
def check_collision(obj1, obj2, width, height):
    return obj1.x < obj2.x + width and obj1.x + width > obj2.x and obj1.y < obj2.y + height and obj1.y + height > obj2.y


# Constants for levels
LEVEL_DURATION = 5 * 60 * 60
NUM_LEVELS = 5

# Creating player and enemies
player = Player(WIDTH // 2, HEIGHT - 60, player_img)
enemies = [Enemy(x * 60, y * 60, enemy_imgs[i % len(enemy_imgs)], enemy_type=i % 3 + 1) for i, (x, y) in enumerate([(x, y) for y in range(2) for x in range(10)])]

# Placeholder for boss sprite
boss_sprite_path = "Boss1.png"  # You can replace this with the actual boss sprite
boss_sprite = pygame.image.load(boss_sprite_path)
boss_sprite = pygame.transform.scale(boss_sprite, (100, 100))  # You can adjust the scale
boss_enemy = Enemy(WIDTH // 2, HEIGHT // 4, boss_sprite, is_boss=True)


# Main game loop
def main():
    FIRE_COOLDOWN = 10  # The number of frames between shots
    fire_cooldown = 0  # Initialize the cooldown variable

    # Re-initialize player and enemies
    player = Player(WIDTH // 2, HEIGHT - 60, player_img)
    enemies = [Enemy(x * 60, y * 60, enemy_imgs[i % len(enemy_imgs)], enemy_type=i % 3 + 1) for i, (x, y) in
               enumerate([(x, y) for y in range(2) for x in range(10)])]
    boss_enemy = Enemy(WIDTH // 2, HEIGHT // 4, boss_sprite, is_boss=True)

    run = True
    clock = pygame.time.Clock()
    enemy_bullet_timer = 0
    boss_bullet_timer = 0
    enemy_speed = 5
    level_timer = 0
    current_level = 1
    enemy_bullets = []
    player.health = 5
    level_font = pygame.font.SysFont(None, 36)

    # Play the intro sound effect
    intro_sound.play()

    # Play the background music
    pygame.mixer.music.load('spaceinvaders1.mpeg')
    pygame.mixer.music.play(-1)  # The -1 means the music will loop indefinitely

    while run:
        win.blit(background_img, (0, 0))
        level_text = level_font.render(f"Level: {current_level}", True, (255, 255, 255))
        win.blit(level_text, (10, 10))

        # win.fill((0,0,0))
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
        # Replenish enemies if all are shot down and increase speed
        if not enemies:
            enemy_speed += 1
            current_level += 1
            enemies = [Enemy(x * 60, y * 60, enemy_imgs[i % len(enemy_imgs)], enemy_type=i % 3 + 1) for i, (x, y) in enumerate([(x, y) for y in range(2) for x in range(10)])]

        # Drawing and moving enemies
        for enemy in enemies[:]:
            enemy.draw(win)
            enemy.move()

            # Collision between enemy sprite and player sprite
            if check_collision(enemy, player, 50, 50):
                player.health = 0  # Wipe out all health of the player
                if game_over_screen():
                    main()
                return
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Update player's position based on mouse position
        player.x = mouse_x - 25  # Center the sprite on the cursor
        player.y = mouse_y - 25

        # Get the state of all keyboard buttons
        keys = pygame.key.get_pressed()

        # Drawing the player
        player.draw(win)

        # Player controls
        if keys[K_LEFT] and player.x > 0:
            player.x -= 5
        if keys[K_RIGHT] and player.x < WIDTH - 50:
            player.x += 5
        if keys[K_UP] and player.y > 0:  # Adding control for upward movement
            player.y -= 5
        if keys[K_DOWN] and player.y < HEIGHT - 50:  # Adding control for downward movement
            player.y += 5
        # In the main function
        # Reduce the cooldown by 1 each frame
        if fire_cooldown > 0:
            fire_cooldown -= 1


        # Check for firing input and cooldown status
        if keys[K_SPACE] and fire_cooldown == 0:
            # Create two bullets spread horizontally
            player.bullets.append(Bullet(player.x + -6, player.y, img=bullet_img, direction=1))
            player.bullets.append(Bullet(player.x + 30, player.y, img=bullet_img, direction=1))
            fire_cooldown = FIRE_COOLDOWN  # Reset the cooldown
            # Play the shooting sound
            shoot_sound.play()

        # Enemy firing bullets
        if enemy_bullet_timer == 0:
            for enemy in enemies:
                enemy.fire_bullet(enemy_bullets)
            enemy_bullet_timer = 30
        else:
            enemy_bullet_timer -= 1

        # Drawing and moving player bullets
        for bullet in player.bullets[:]:
            bullet.move()
            bullet.draw(win)
            if bullet.y < 0:
                player.bullets.remove(bullet)

                # Drawing and moving enemy bullets
        for bullet in enemy_bullets[:]:
            bullet.move()
            bullet.draw(win)
            if bullet.y > HEIGHT:
                enemy_bullets.remove(bullet)

        # Drawing and moving enemies
        for enemy in enemies:
            enemy.draw(win)
            enemy.move(    )

            # Collision between player bullets and enemies
            for bullet in player.bullets:
                if check_collision(bullet, enemy, 5, 10):
                    player.bullets.remove(bullet)
                    enemies.remove(enemy)
                    # Play the explosion sound
                    explosion_sound.play()
                    break

            # Collision between enemy bullets and player
            for bullet in enemy_bullets[:]:
                if check_collision(bullet, player, 5, 50):
                    enemy_bullets.remove(bullet)
                    playerhit_sound.play()
                    player.health -= 1
                    if player.health <= 0:
                        if game_over_screen():
                            main()
                        return

        # Level progression logic
        level_timer += 1
        if level_timer == LEVEL_DURATION:
            current_level += 1
            level_timer = 0
            level_text = level_font.render(f"Level: {current_level}", True, (255, 255, 255))  # Create level text
            win.blit(level_text, (10, 10))  # Draw the level text on the window
            pygame.display.update()
            if current_level > NUM_LEVELS:
                print("You have won the game!")
                run = False
                break
            # Adjust difficulty as per current_level
            # Add the boss_enemy in Level 5

        # Boss fight logic (if required)
        if current_level == 5:
            boss_enemy.draw(win)
            boss_enemy.move()
            # Additional logic for boss behavior
            # Boss firing bullets (4 streams)
            if boss_bullet_timer == 0:
                for angle in [0, 90, 180, 270]:
                    boss_enemy.fire_bullet(enemy_bullets)
                boss_bullet_timer = 60  # adjust the timer as per the required firing rate
            else:
                boss_bullet_timer -= 1
        # Updating the display
        pygame.display.update()

    pygame.quit()


# Running the main game loop
main()
