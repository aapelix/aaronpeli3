import pygame

class Camera:
    def __init__(self, width, height, target=None, smoothing=0.1):
        """
        Initialize a smooth-following camera for a Pygame game

        :param width: Screen width
        :param height: Screen height
        :param target: Target sprite to follow (typically the player)
        :param smoothing: Camera movement smoothing factor (0-1, lower is smoother)
        """
        self.camera = pygame.math.Vector2(0, 0)
        self.screen_width = width
        self.screen_height = height
        self.target = target
        self.smoothing = smoothing

    def set_target(self, target):
        """
        Set the target for the camera to follow

        :param target: Sprite to follow
        """
        self.target = target

    def update(self):
        """
        Update camera position smoothly following the target
        """
        if not self.target:
            return

        # Calculate target position (center of the target)
        target_x = self.target.rect.centerx - self.screen_width // 2
        target_y = self.target.rect.centery - self.screen_height // 2

        # Smooth interpolation
        self.camera.x += (target_x - self.camera.x) * self.smoothing
        self.camera.y += (target_y - self.camera.y) * self.smoothing

    def apply(self, entity):
        """
        Apply camera offset to an entity's position

        :param entity: Sprite to adjust
        :return: Adjusted rect for drawing
        """
        return entity.rect.move(-int(self.camera.x), -int(self.camera.y))

    def apply_rect(self, rect):
        """
        Apply camera offset to a rect

        :param rect: Pygame rect to adjust
        :return: Adjusted rect
        """
        return rect.move(-int(self.camera.x), -int(self.camera.y))