import pygame
import random

class Enemy(pygame.sprite.Sprite):
    DINOSAUR_TYPES = [
        "cole", "kira", "kuro", "loki",
        "mono", "nico", "olaf", "sena",
    ]

    ACTION_FRAME_COUNTS = {
        'idle': 3,
        'bite': 3,
        'move': 6
    }

    def __init__(self, position, health=100):
        super().__init__()
        self.dino_type = random.choice(self.DINOSAUR_TYPES)  # Randomize dinosaur type
        self.animations = self.load_animations()  # Load animations based on type

        self.image = self.animations['idle'][0]  # Start with idle animation
        self.rect = self.image.get_rect(topleft=position)
        self.health = health
        self.speed = 2

        self.attack_cooldown = 1000
        self.last_attack_time = 0

        # Animation settings
        self.current_animation = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.2
        self.player = None

    def load_animations(self):
        """
        Load animation frames for the selected dinosaur type.
        Returns a dictionary of animations.
        """
        animations = {}
        scale_factor = 2

        for action, frame_count in self.ACTION_FRAME_COUNTS.items():
            path = f"assets/sprites/dinosaurs/{self.dino_type}/base/{action}.png"
            spritesheet = pygame.image.load(path).convert_alpha()

            frame_width = spritesheet.get_width() // frame_count
            frame_height = spritesheet.get_height()

            frames = []
            for i in range(frame_count):
                frame = spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height))

                # Scale the frame
                scaled_frame = pygame.transform.scale(
                    frame,
                    (frame_width * scale_factor, frame_height * scale_factor)
                )
                frames.append(scaled_frame)

            animations[action] = frames
        return animations

    def animate(self):
        """
        Handle animation cycling.
        """
        frames = self.animations[self.current_animation]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(frames):
            self.frame_index = 0

        self.image = frames[int(self.frame_index)]

        # Flip the image if moving to the left (direction.x < 0)
        if self.rect.x < self.player.rect.x:  # Player is to the right
            self.image = pygame.transform.flip(frames[int(self.frame_index)], False, False)
        else:  # Player is to the left
            self.image = pygame.transform.flip(frames[int(self.frame_index)], True, False)

    def take_damage(self, amount):
        self.health -= amount
        self.player.coins = self.player.coins + amount
        if self.health <= 0:
            self.kill()  # Remove the enemy when it dies
            self.player.kills = self.player.kills + 1

    def update(self, player):
        """
        Update the enemy's behavior: move towards the player and animate.
        """

        if self.player is None:
            self.player = player

        # Vector to player
        direction = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        if direction.length() > 0:  # Avoid dividing by zero
            direction = direction.normalize()

        # Movement speed
        self.rect.x += direction.x * self.speed
        self.rect.y += direction.y * self.speed

        # Set current animation to "move"

        if direction.x != 0 and direction.y != 0:
            self.current_animation = 'move'

        self.animate()

    def attack_player(self, player):
        """
        Deal damage to the player if within attack range and cooldown allows.
        """
        current_time = pygame.time.get_ticks()
        attack_range = 30


        if self.rect.colliderect(player.rect.inflate(attack_range, attack_range)):
            if current_time - self.last_attack_time >= self.attack_cooldown:
                player.take_damage(10)
                self.last_attack_time = current_time

                # Set current animation to "bite" when attacking
                self.current_animation = 'bite'
                self.frame_index = 0  # Reset animation frame index

