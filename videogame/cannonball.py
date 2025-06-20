"""playership"""

import pygame
from videogame import assets
from videogame import rgbcolors

class RectSurface(pygame.Surface):
    def __init__(
     self, width, height, color, background_color = rgbcolors.white, name = "None"       
    ):
        super().__init__((width, height))
        self._color = color
        self._name = name
        self.fill(background_color)
        #uncomment if surfaces with same color will overlap
        #self.set_colorkey(background_color)
        self._rect_width = width
        self._rect_height = height
        rectangle = pygame.Rect(0, 0, self._rect_width, self._rect_height)
        pygame.draw.rect(self, self._color, rectangle)

    @property
    def height(self):
        return self._rect_height

    @property
    def width(self):
        return self._rect_width

    @property
    def rect(self):
        return self.get_rect()
    
class CannonBallSprite(pygame.sprite.Sprite):
    def __init__(
            self, position, direction, speed, width, height, 
            color, name = "None", image_path = 'cannon ball'
    ):
        super().__init__()
        self._ship_image = RectSurface(width = width, height = height, color = color, name = name)
        self._png_image = pygame.image.load(assets.get(image_path)).convert_alpha()
        self.image = self._png_image
        self._start_position = (position.x, position.y)
        self.rect = self.image.get_rect()
        self.rect.center = (position.x, position.y)
        self._direction = direction
        self._speed = speed
        self._width = width
        self._height = height
        self._color = color

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def position(self):
        return pygame.math.Vector2(self.rect.center)

    @position.setter
    def position(self, new_position):
        if not isinstance(new_position, pygame.math.Vector2):
            raise TypeError("new_position doesn't match self._position")
        self.rect.center = new_position


    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        if not isinstance(new_direction, type(self._direction)):
            raise TypeError("new_direction doesn't match self._direction")
        self._direction = new_direction

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, new_speed):
        self._speed = new_speed

    @property
    def velocity(self):
        return self._direction * self._speed

    @velocity.setter
    def velocity(self, new_velocity):
        if not isinstance(new_velocity, pygame.math.Vector2):
            raise TypeError("new_velocity doesn't match self.velocity()")
        self._speed = new_velocity.length()
        self._direction = new_velocity

    def move_ip(self, x, y):
        """Move paddle in place"""
        self.position += pygame.math.Vector2(x, y)

    def __repr__(self):
        """Cannon Ball sprite in string form."""
        stringify = f"PaddleSrite({repr(self.position)}, "
        f"{repr(self.speed)}, {repr(self.width)}, {repr(self.height)}, "
        f'{repr(self._color)}, "{repr(self.position)}")'
        return stringify