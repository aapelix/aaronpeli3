import pygame
import math

class BaseWeapon(pygame.sprite.Sprite):
    def __init__(self, image_path, owner, scale=1, offset=(0, 0)):
        """
        Base weapon class for all weapon types

        :param image_path: Path to weapon image
        :param owner: Player sprite that holds the weapon
        :param scale: Scale factor for the weapon image (default 1)
        :param offset: Tuple (x_offset, y_offset) to adjust weapon position relative to owner
        """
        super().__init__()

        # Load weapon image
        original_image = pygame.image.load(image_path).convert_alpha()

        # Scale the image
        original_width = original_image.get_width()
        original_height = original_image.get_height()
        new_width = int(original_width / scale)
        new_height = int(original_height / scale)

        self.original_image = pygame.transform.scale(original_image, (new_width, new_height))
        self.image = self.original_image
        self.rect = self.image.get_rect()

        # Weapon properties
        self.owner = owner
        self.offset = offset
        self.damage = 10
        self.fire_rate = 500  # Milliseconds between shots
        self.last_shot_time = 0

        # Projectile properties
        self.projectiles = pygame.sprite.Group()

    def rotate_to_mouse(self, camera=None):
        """
        Rotate weapon to face the mouse cursor and flip when the rotation angle exceeds ±90 degrees.

        :param camera: Optional camera object to account for screen offset
        """
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # If camera is provided, adjust mouse position
        if camera:
            mouse_x += int(camera.camera.x)
            mouse_y += int(camera.camera.y)

        # Get weapon position relative to camera
        weapon_x = self.owner.rect.centerx + self.offset[0]
        weapon_y = self.owner.rect.centery + self.offset[1]

        # Calculate the angle to the mouse
        angle = math.degrees(math.atan2(mouse_y - weapon_y, mouse_x - weapon_x))

        # Determine if the weapon should be flipped
        flip = angle > 90 or angle < -90

        # Rotate the weapon image
        rotated_image = pygame.transform.rotate(self.original_image, angle if flip else -angle)

        # Flip the image if needed
        if flip:
            rotated_image = pygame.transform.flip(rotated_image, False, True)  # Flip vertically

        # Update the weapon's image and rect
        self.image = rotated_image
        self.rect = self.image.get_rect(center=(weapon_x, weapon_y))

    def shoot(self):
        """
        Base shooting method to be overridden by specific weapon types

        :return: True if shot successful, False otherwise
        """
        current_time = pygame.time.get_ticks()

        # Check fire rate
        if current_time - self.last_shot_time < self.fire_rate:
            return False

        self.last_shot_time = current_time
        return True

    def update(self, camera=None):
        """
        Update weapon position and rotation
        """
        self.rotate_to_mouse()

        self.rotate_to_mouse(camera)

        # Update any active projectiles
        self.projectiles.update()

    def draw(self, surface):
        """
        Draw weapon and its projectiles

        :param surface: Pygame surface to draw on
        """


        surface.blit(self.image, self.rect)
        self.projectiles.draw(surface)