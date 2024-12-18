import pygame
import random
from sprite import AnimatedSprite
from camera import Camera
from enemy import Enemy
from health_bar import HealthBar
import asyncio

class Game:
    def __init__(self, width=800, height=600):
        """
        Initialize Pygame and game window

        :param width: Window width
        :param height: Window height
        """
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("aaronpeli3")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Sprite sheet configuration
        spritesheet_config = {
            'idle': {
                'file': './assets/sprites/player_idle.png',
                'frame_width': 16,
                'frame_height': 16,
                'frame_count': 2
            },
            'idle_left': {
                'file': './assets/sprites/player_idle.png',  # Reuse idle animation
                'frame_width': 16,
                'frame_height': 16,
                'frame_count': 2
            },
            'run_right': {
                'file': './assets/sprites/player_run.png',
                'frame_width': 16,
                'frame_height': 16,
                'frame_count': 6
            },
            'run_left': {
                'file': './assets/sprites/player_run.png',
                'frame_width': 16,
                'frame_height': 16,
                'frame_count': 6
            },
            'run_up': {
                'file': './assets/sprites/player_run.png',
                'frame_width': 16,
                'frame_height': 16,
                'frame_count': 6
            },
            'run_down': {
                'file': './assets/sprites/player_run.png',
                'frame_width': 16,
                'frame_height': 16,
                'frame_count': 6
            }
        }

        # Create player
        self.player = AnimatedSprite((400, 300), spritesheet_config)
        self.all_sprites = pygame.sprite.Group(self.player)
        self.enemies = pygame.sprite.Group()


        for enemy in self.enemies:
            enemy.health_bar = HealthBar(enemy, max_width=50, height=5, offset_y=-10)
        self.player.health_bar = HealthBar(self.player, max_width=70, height=7, offset_y=-15)

        # Add projectiles group for all game projectiles
        self.projectiles = pygame.sprite.Group()

        # Set up the enemy spawn timer (e.g., every 5 seconds)
        self.SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_ENEMY_EVENT, 5000)  # 5000 ms = 5 seconds

        self.camera = Camera(self.screen.get_width(), self.screen.get_height(),
            target=self.player, smoothing=0.1)


        self.play_button = pygame.Rect(350, 400, 100, 50)  # Simple button rect
        self.title_screen = True  # Flag to show title screen

    def create_enemy(self, position):
        """Create a new enemy at the given position."""
        enemy = Enemy(position)
        # Add health bar to the enemy immediately when created
        enemy.health_bar = HealthBar(enemy, max_width=50, height=5, offset_y=-10)
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)

    def spawn_random_enemy(self):
        """Spawn an enemy at a random position."""
        random_x = random.randint(0, self.screen.get_width())
        random_y = random.randint(0, self.screen.get_height())
        self.create_enemy((random_x, random_y))

    def handle_player_enemy_collision(self):
        """
        Handle collisions between the player and enemies.
        Prevents overlapping and pushes sprites apart.
        """
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):

                # Determine overlap in x and y directions
                if self.player.rect.centerx - 10 < enemy.rect.centerx:
                    overlap_x = (self.player.rect.right - enemy.rect.left)
                else:
                    overlap_x = -(enemy.rect.right - self.player.rect.left)

                if self.player.rect.centery - 10 < enemy.rect.centery:
                    overlap_y = (self.player.rect.bottom - enemy.rect.top)
                else:
                    overlap_y = -(enemy.rect.bottom - self.player.rect.top)

                # Move sprites apart based on the smallest overlap
                if abs(overlap_x) < abs(overlap_y):
                    self.player.rect.x -= overlap_x
                    enemy.rect.x += overlap_x
                else:
                    self.player.rect.y -= overlap_y
                    enemy.rect.y += overlap_y

    def draw_title_screen(self):
        """
        Draw the title screen with the play button and idle player sprite.
        """
        self.screen.fill((0, 0, 0))  # Black background

        # Load the title image
        title_image = pygame.image.load('./assets/img.png').convert_alpha()
        title_rect = title_image.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_image, title_rect)

        # Draw the play button
        pygame.draw.rect(self.screen, (255, 255, 255), self.play_button)
        play_text = self.font.render("Play", True, (0, 0, 0))
        self.screen.blit(play_text, (self.play_button.x + (self.play_button.width // 2) - (play_text.get_width() // 2),
                                     self.play_button.y + (self.play_button.height // 2) - (play_text.get_height() // 2)))

        pygame.display.flip()

    def handle_title_screen_events(self):
        """
        Handle events on the title screen, e.g., clicking the play button.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button.collidepoint(event.pos):
                    self.title_screen = False  # Start the game
        return True

    async def run(self):
        """
        Main game loop
        """
        running = True
        while running:
            if self.title_screen:
                if not self.handle_title_screen_events():
                    return
                self.draw_title_screen()
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == self.SPAWN_ENEMY_EVENT:
                        self.spawn_random_enemy()

                # Update camera and game state
                self.camera.update()
                for sprite in self.all_sprites:
                    if isinstance(sprite, Enemy):
                        sprite.update(self.player)
                        sprite.attack_player(self.player)
                    else:
                        sprite.update(self.camera)

                    if hasattr(sprite, 'health_bar'):
                        sprite.health_bar.draw(self.screen, self.camera)

                self.handle_player_enemy_collision()

                if self.player.current_weapon:
                    self.projectiles.add(self.player.current_weapon.projectiles)

                for projectile in self.projectiles:
                    hit_enemies = pygame.sprite.spritecollide(projectile, self.enemies, False)
                    for enemy in hit_enemies:
                        enemy.take_damage(projectile.damage)
                        projectile.kill()

                for enemy in self.enemies:
                    enemy.update(self.player)
                    enemy.attack_player(self.player)

                # Draw game screen
                self.screen.fill((0, 0, 0))

                for sprite in self.all_sprites:
                    self.screen.blit(sprite.image, self.camera.apply(sprite))

                if hasattr(self.player, 'health_bar'):
                    self.player.health_bar.draw(self.screen, self.camera)

                for enemy in self.enemies:
                    if hasattr(enemy, 'health_bar'):
                        enemy.health_bar.draw(self.screen, self.camera)

                # Draw weapon and projectiles
                if self.player.current_weapon:
                    weapon_rect = self.camera.apply_rect(self.player.current_weapon.rect)
                    self.screen.blit(self.player.current_weapon.image, weapon_rect)

                for projectile in self.projectiles:
                    projectile_rect = self.camera.apply_rect(projectile.rect)
                    self.screen.blit(projectile.image, projectile_rect)

                kills_text = self.font.render(f"Kills: {self.player.kills}", True, (0, 0, 0))
                coins_text = self.font.render(f"Coins: {self.player.coins}", True, (0, 0, 0))

                self.screen.blit(kills_text, (10, 10))
                self.screen.blit(coins_text, (10, 40))

                pygame.display.flip()

                self.clock.tick(60)

            await asyncio.sleep(0)

        pygame.quit()

class Character:
    def __init__(self, x, y, image_files):
        self.x = x
        self.y = y
        self.image_files = image_files  # List of images for the idle animation
        self.frames = [pygame.image.load(img).convert_alpha() for img in image_files]
        self.current_frame = 0
        self.frame_rate = 0.2  # Delay between frames (adjust this value for speed)
        self.time_since_last_frame = 0  # Time accumulator for frame updates

    def update(self, delta_time):
        """Update the current frame for animation based on time."""
        self.time_since_last_frame += delta_time
        if self.time_since_last_frame >= self.frame_rate:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.time_since_last_frame = 0  # Reset the frame update timer

    def draw(self, screen):
        """Draw the current frame on the screen at its position."""
        screen.blit(self.frames[self.current_frame], (self.x, self.y))
