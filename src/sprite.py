import pygame

from src.weapons.flamethrower import Flamethrower
from src.weapons.laser_gun import LaserGun
from src.weapons.pistol import Pistol
from src.weapons.shotgun import Shotgun

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, position, spritesheet_config, scale=2):
        """
        Initialize an animated sprite with configurable sprite sheets and animation logic

        :param position: Starting (x, y) position of the sprite
        :param spritesheet_config: Dictionary containing animation configurations
        :param scale: Scaling factor for the sprite frames
        """
        super().__init__()

        # Animation configuration
        self.animations = {}
        self.current_animation = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.2  # Controls animation speed
        self.scale = scale  # Scaling factor

        # Load sprite sheets and configure animations
        self.load_animations(spritesheet_config)

        # Current image and rect
        self.image = self.animations[self.current_animation][0]
        self.rect = self.image.get_rect(topleft=position)

        # Movement attributes
        self.speed = 5
        self.velocity = pygame.math.Vector2(0, 0)
        self.last_facing_direction = 'right'

        # Weapon management
        self.weapons = []
        self.current_weapon = None

        self.weapon_switch_cooldown = 300  # Milliseconds
        self.last_weapon_switch_time = 0

        # Initialize default weapon
        self.add_weapon('flamethrower')
        self.add_weapon('shotgun')
        self.add_weapon('pistol')
        self.add_weapon('laser_gun')

        self.health = 100

        self.camera = None

        self.kills = 0
        self.coins = 0

    def load_animations(self, spritesheet_config):
        """
        Load sprite sheets and split them into individual frames

        :param spritesheet_config: Dictionary with animation configurations
        """
        for animation_name, config in spritesheet_config.items():
            spritesheet = pygame.image.load(config['file']).convert_alpha()
            frame_width = config['frame_width']
            frame_height = config['frame_height']

            frames = []
            for i in range(config['frame_count']):
                frame = spritesheet.subsurface(
                    (i * frame_width, 0, frame_width, frame_height)
                )
                # Scale frame
                scaled_frame = pygame.transform.scale(
                    frame,
                    (frame_width * self.scale, frame_height * self.scale)
                )
                frames.append(scaled_frame)

            self.animations[animation_name] = frames

    def animate(self):
        """
        Handle sprite animation cycling
        """
        # Get current animation frames
        animation_frames = self.animations[self.current_animation]

        # Increment frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation_frames):
            self.frame_index = 0

        # Update current image
        self.image = animation_frames[int(self.frame_index)]

        if self.current_animation == 'run_left':
            self.image = pygame.transform.flip(self.image, True, False)

        if self.current_animation == 'idle_left':
            self.image = pygame.transform.flip(self.image, True, False)

        if self.current_animation == 'run_up' and self.last_facing_direction == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

        if self.current_animation == 'run_down' and self.last_facing_direction == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def add_weapon(self, weapon_type):
        """
        Add a new weapon to the player's inventory

        :param weapon_type: Type of weapon to add ('flamethrower' or 'shotgun')
        """
        if weapon_type == 'flamethrower':
            weapon = Flamethrower(self)
        elif weapon_type == 'shotgun':
            weapon = Shotgun(self)
        elif weapon_type == 'pistol':
            weapon = Pistol(self)
        elif weapon_type == "laser_gun":
            weapon = LaserGun(self)
        else:
            raise ValueError(f"Unknown weapon type: {weapon_type}")

        self.weapons.append(weapon)

        # Set as current weapon if none exists
        if self.current_weapon is None:
            self.current_weapon = weapon

    def switch_weapon(self):
        """
        Cycle through available weapons with a cooldown
        """
        current_time = pygame.time.get_ticks()

        # Check if enough time has passed since last switch
        if current_time - self.last_weapon_switch_time < self.weapon_switch_cooldown:
            return

        if not self.weapons:
            return

        # Update last switch time
        self.last_weapon_switch_time = current_time

        # Cycle to next weapon
        current_index = self.weapons.index(self.current_weapon)
        next_index = (current_index + 1) % len(self.weapons)
        self.current_weapon = self.weapons[next_index]

    def handle_input(self, camera=None):
        """
        Handle player input and set appropriate animation

        :param camera: Optional camera object
        """
        keys = pygame.key.get_pressed()

        # Reset velocity
        self.velocity.x = 0
        self.velocity.y = 0

        # Movement and animation logic
        if keys[pygame.K_a]:
            self.velocity.x = -self.speed
            self.current_animation = 'run_left'
            self.last_facing_direction = 'left'
        elif keys[pygame.K_d]:
            self.velocity.x = self.speed
            self.current_animation = 'run_right'
            self.last_facing_direction = 'right'

        if keys[pygame.K_w]:
            self.velocity.y = -self.speed
            self.current_animation = 'run_up'
        elif keys[pygame.K_s]:
            self.velocity.y = self.speed
            self.current_animation = 'run_down'

        # Set to idle if no movement
        if self.velocity.length() == 0:
            if self.last_facing_direction == 'left':
                self.current_animation = 'idle_left'
            else:
                self.current_animation = 'idle'

        if keys[pygame.K_f]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_weapon_switch_time >= self.weapon_switch_cooldown:
                self.switch_weapon()

        # Shooting
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and self.current_weapon:
            self.current_weapon.shoot()


    def update(self, camera=None):
        """
        Update player sprite and current weapon
        """
        self.handle_input()
        self.animate()

        # Move sprite
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        self.camera = camera

        # Update current weapon
        if self.current_weapon:
            self.current_weapon.update(self.camera)
        

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            print("Player is dead")  # Replace with proper game over logic
