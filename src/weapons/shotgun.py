import pygame
import math
import random
from src.weapons.base_weapon import BaseWeapon


class Pellet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((3, 3))
        self.image.fill((50, 50, 50))

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 15

        self.damage = 10

        # Add spread to pellets
        spread = random.uniform(-10, 10)
        radians = math.radians(angle + spread)

        self.velocity = pygame.math.Vector2(
            math.cos(radians) * self.speed,
            math.sin(radians) * self.speed
        )

        self.lifetime = 60  # Frames

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Remove after lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


class Shotgun(BaseWeapon):
    def __init__(self, owner):
        super().__init__('assets/sprites/shotgun.png', owner, scale=1, offset=(0, 4))

        self.fire_rate = 800
        self.pellet_count = 8

    def shoot(self):
        """
        Shoot multiple pellets in a spread
        """
        if not super().shoot():
            return False

        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.owner.camera:
            mouse_x += int(self.owner.camera.camera.x)
            mouse_y += int(self.owner.camera.camera.y)

        weapon_x = self.owner.rect.centerx
        weapon_y = self.owner.rect.centery

        angle = math.degrees(math.atan2(mouse_y - weapon_y, mouse_x - weapon_x))

        for _ in range(self.pellet_count):
            pellet = Pellet(weapon_x, weapon_y, angle)
            self.projectiles.add(pellet)

        return True
