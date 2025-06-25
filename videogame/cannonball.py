"""Cannonball creation here"""

import pygame
from videogame import assets
from videogame import rgbcolors


class CannonBallSurface(pygame.Surface):
    """Create ball surface"""
    def __init__(self, radius, color, background_color=rgbcolors.black, name="None"):
        width = 2 * radius
        super().__init__((width, width))
        center = (radius, radius)
        self._color = color
        self._name = name
        self._radius = radius
        self.fill(background_color)
        # uncomment if surfaces with same color will overlap
        # self.set_colorkey(background_color)

        pygame.draw.circle(self, self._color, center, radius)

    @property
    def radius(self):
        """return ball radius"""
        return self._radius

    @property
    def rect(self):
        """Return rect surface of ball"""
        return self.get_rect()


class CannonBallSprite(pygame.sprite.Sprite):
    """Sprite for cannonball"""
    def __init__(
        self,
        position,
        direction,
        speed,
        radius,
        color,
        name="None",
        image_path="cannon ball",
    ):
        super().__init__()
        self._cannon_ball_image = CannonBallSurface(
            radius, color, rgbcolors.black, name
        )
        self._png_image = pygame.image.load(assets.get(image_path)).convert_alpha()
        self._scaled_image = pygame.transform.smoothscale(
            self._png_image, (radius, radius)
        )
        self.image = self._scaled_image
        self._start_position = position
        self.rect = self.image.get_rect()
        self.rect.center = (position.x, position.y)
        self._direction = direction
        self._speed = speed
        self._radius = radius
        self._color = color
        self._name = name

    @property
    def radius(self):
        """Return Cannonball sprite radius"""
        return self._radius

    @property
    def position(self):
        """return position"""
        return pygame.math.Vector2(self.rect.center)

    @position.setter
    def position(self, new_position):
        """Set new position"""
        if not isinstance(new_position, pygame.math.Vector2):
            raise TypeError("new_position doesn't match self._position")
        self.rect.center = (new_position.x, new_position.y)

    @property
    def direction(self):
        """Return direction"""
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        """Set new direction"""
        if not isinstance(new_direction, pygame.math.Vector2):
            raise TypeError("new_direction doesn't match self._direction")
        self._direction = new_direction

    @property
    def speed(self):
        """Return speed"""
        return self._speed

    @speed.setter
    def speed(self, new_speed):
        """Set new speed"""
        if not isinstance(new_speed, type(self._speed)):
            raise TypeError("new_speed does not match the type of self._speed")
        self._speed = new_speed

    @property
    def velocity(self):
        """Return velocity"""
        return self._direction * self._speed

    @velocity.setter
    def velocity(self, new_velocity):
        """Set new velocity"""
        if not isinstance(new_velocity, pygame.math.Vector2):
            raise TypeError("new_velocity doesn't match self.velocity()")
        self._speed = new_velocity.length()
        self._direction = new_velocity.normalize()

    def move_ip(self, x, y):
        """Move in place"""
        self.position = self.position + pygame.math.Vector2(x, y)

    def __repr__(self):
        """CannonBallSprite stringify."""
        stringify = f"CannonBallSprite({repr(self.position)}, "
        f"{repr(self.speed)}, {repr(self.radius)}, "
        f'{repr(self._color)}, "{repr(self.position)}")'
        return stringify
