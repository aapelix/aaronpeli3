import pygame
import random
from sprite import AnimatedSprite
from camera import Camera
from enemy import Enemy
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

        # Add projectiles group for all game projectiles
        self.projectiles = pygame.sprite.Group()

        # Set up the enemy spawn timer (e.g., every 5 seconds)
        self.SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_ENEMY_EVENT, 5000)  # 5000 ms = 5 seconds

        self.camera = Camera(self.screen.get_width(), self.screen.get_height(),
            target=self.player, smoothing=0.1)

    def create_enemy(self, position):
        """Create a new enemy at the given position."""
        enemy = Enemy(position)
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
                # Calculate overlap and push sprites apart
                overlap_x = 0
                overlap_y = 0

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

    async def run(self):
        """
        Main game loop
        """
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == self.SPAWN_ENEMY_EVENT:
                    self.spawn_random_enemy()  # Spawn enemy every 5 seconds


            # Update
            self.camera.update()
            # In the drawing section of the run method
            for sprite in self.all_sprites:
                if isinstance(sprite, Enemy):
                    sprite.update(self.player)
                    sprite.attack_player(self.player)
                else:
                    sprite.update(self.camera)

            self.handle_player_enemy_collision()

            # Collect all projectiles from current weapon
            if self.player.current_weapon:
                self.projectiles.add(self.player.current_weapon.projectiles)

            for projectile in self.projectiles:
                hit_enemies = pygame.sprite.spritecollide(projectile, self.enemies, False)
                for enemy in hit_enemies:
                    enemy.take_damage(projectile.damage)
                    projectile.kill()

            for enemy in self.enemies:
                enemy.update(self.player)  # Pass the player to update logic
                enemy.attack_player(self.player)  # Check and attack the player

            # Draw
            self.screen.fill((255, 255, 255))  # White background

            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))

                # Draw current weapon
            if self.player.current_weapon:
                weapon_rect = self.camera.apply_rect(self.player.current_weapon.rect)
                self.screen.blit(self.player.current_weapon.image, weapon_rect)

                # Draw projectiles with camera offset
            for projectile in self.projectiles:
                projectile_rect = self.camera.apply_rect(projectile.rect)
                self.screen.blit(projectile.image, projectile_rect)

            kills_text = self.font.render(f"Kills: {self.player.kills}", True, (0, 0, 0))  # Black text
            coins_text = self.font.render(f"Coins: {self.player.coins}", True, (0, 0, 0))  # Black text

            self.screen.blit(kills_text, (10, 10))
            self.screen.blit(coins_text, (10, 40))

            pygame.display.flip()

            # Cap the frame rate
            self.clock.tick(60)

            await asyncio.sleep(0)

        pygame.quit()
