import pygame


class HealthBar:
    def __init__(self, entity, max_width=50, height=5, offset_y=-10):
        """
        Initialize a health bar for an entity

        :param entity: The sprite the health bar is attached to
        :param max_width: Maximum width of the health bar
        :param height: Height of the health bar
        :param offset_y: Vertical offset from the entity's top
        """
        self.entity = entity
        self.max_width = max_width
        self.height = height
        self.offset_y = offset_y

        # Store the initial max health
        self.max_health = entity.health if hasattr(entity, 'health') else 100

    def draw(self, surface, camera=None):
        """
        Draw the health bar on the given surface

        :param surface: Pygame surface to draw on
        :param camera: Optional camera for offset calculation
        """
        # Ensure the entity has a health attribute
        if not hasattr(self.entity, 'health'):
            return

        # Calculate current health percentage
        health_percentage = max(0, self.entity.health / self.max_health)
        current_width = int(self.max_width * health_percentage)

        # Determine position
        if camera:
            # Use camera's apply method to get the correct screen position
            entity_rect = camera.apply(self.entity)
            x = entity_rect.centerx - self.max_width // 2
            y = entity_rect.top + self.offset_y
        else:
            # Fallback to entity's rect if no camera
            x = self.entity.rect.centerx - self.max_width // 2
            y = self.entity.rect.top + self.offset_y

        # Color gradient from red to green based on health
        if health_percentage > 0.5:
            # Green to yellow (fading green)
            red = int(255 * (1 - (health_percentage - 0.5) * 2))
            color = (red, 255, 0)
        else:
            # Yellow to red (increasing red)
            green = int(255 * health_percentage * 2)
            color = (255, green, 0)

        # Draw background (dark gray)
        bg_rect = pygame.Rect(x, y, self.max_width, self.height)
        pygame.draw.rect(surface, (50, 50, 50), bg_rect)

        # Draw health bar
        health_rect = pygame.Rect(x, y, current_width, self.height)
        pygame.draw.rect(surface, color, health_rect)