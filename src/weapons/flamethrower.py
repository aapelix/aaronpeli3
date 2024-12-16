import pygame
import math
import random
from .base_weapon import BaseWeapon


class FlameParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 128, 0, 200), (10, 10), 5)

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.damage = 15

        spread = random.uniform(-15, 15)
        radians = math.radians(angle + spread)

        self.velocity = pygame.math.Vector2(
            math.cos(radians) * self.speed,
            math.sin(radians) * self.speed
        )

        self.lifetime = 30  # Frames

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Fade out
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


class Flamethrower(BaseWeapon):
    def __init__(self, owner):
        super().__init__('assets/sprites/flamethrower.png', owner, scale=1, offset=(0, 4))

        self.fire_rate = 40
        self.max_particles = 10

    def shoot(self):
        """
        Create flame particles when shooting
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

        for _ in range(self.max_particles):
            particle = FlameParticle(weapon_x, weapon_y, angle)
            self.projectiles.add(particle)

        return True
