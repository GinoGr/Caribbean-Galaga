"""playership"""

from random import randint
import pygame
from videogame import assets
from videogame import rgbcolors

class RectSurface(pygame.Surface):
    def __init__(
     self, width, height, color = rgbcolors.white, background_color = rgbcolors.white, name = "None"       
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
    
class ShipSprite(pygame.sprite.Sprite):
    def __init__(self, position, direction, speed, width, height, name = "None", image_path = 'playership', rotate_angle = False, scale_factor = 1, path = None):
        super().__init__()
        #self._ship_image = RectSurface(width = width, height = height, name = name)
        self._png_image = pygame.image.load(assets.get(image_path)).convert_alpha()
        self.rotated_scaled_image = pygame.transform.smoothscale(self._png_image, (width, height))
        if rotate_angle:
            self.rotated_scaled_image = pygame.transform.rotozoom(self._png_image, 180, scale_factor)
        self.image = self.rotated_scaled_image
        self._start_position = position
        self._position = position
        self.rect = self.image.get_rect()
        self.rect.center = position
        self._direction = direction
        self._speed = speed
        self._width = width
        self._height = height
        self._name = name
        self._initial_time = pygame.time.get_ticks()
        self._last_fire_time = 0
        self._is_exploading = False
        self._expload_start_time = 0
        self._state = "Idle"
        self._base_path = path

        self._fire_every = randint(5000, 15000)  # Fire every 5-15 seconds

        # Set the hitbox for the ship.
        self.hitbox = pygame.Rect(0, 0, int(self.rect.width * 0.2), int(self.rect.height * 0.7))
        self.hitbox.center = self.rect.center

    def set_final_position(self, position):
        """Set the final position of the ship."""
        if not isinstance(position, type(self._base_path[0])):
            raise TypeError("position must be same type as self._base_path[0]")
        self._base_path[-2] = position
    
    def comes_from_left(self):
        new_base_path = []
        for point in self._base_path:
            new_base_path.append(((point[0] * -1) + 800, point[1]))
        self._base_path = new_base_path
        self._path_progress = 0.0
        self._state = "entering"

    @property
    def base_path(self):
        return self._base_path

    def enable_entry_path(self):
        self._entry_path = self._base_path
        self._path_progress = 0.0
        self._state = "entering"

    def update_entry(self, delta_time):
        if self._state != "entering":
            return
        path = self._entry_path
        segs = len(path) - 3
        u = min(self._path_progress, 0.9999) * segs
        i = int(u)
        local = u - i
        p0, p1, p2, p3 = path[i:i+4]
        self.rect.center = catmull_rom(p0, p1, p2, p3, local)
        self.hitbox.center = self.rect.center
        self._path_progress += delta_time * 0.3
        if self._path_progress >= 1.0:
            self._state = "idle"
            self.position = pygame.math.Vector2(self.rect.center)

    @property
    def hitbox(self):
        """Return the hitbox of the ship."""
        return self._hitbox
    
    @hitbox.setter
    def hitbox(self, new_hitbox):
        """Set the hitbox of the ship."""
        if not isinstance(new_hitbox, pygame.Rect):
            raise TypeError("new_hitbox must be a pygame.Rect")
        self._hitbox = new_hitbox
        self._hitbox.center = self.rect.center
        
    def expload(self, image_name):
        """Switch the ship image to a new image. (explosion, etc.)"""
        self._png_image = pygame.image.load(assets.get(image_name)).convert_alpha()
        self.image = self._png_image
        self.rect = self.image.get_rect()
        self.rect.center = self._position

    @property
    def last_fire_time(self):
        """Return the last fire time of the ship."""
        return self._last_fire_time
    
    @last_fire_time.setter
    def last_fire_time(self, new_fire_time):
        """Set the last fire time of the ship."""
        if not isinstance(new_fire_time, int):
            raise TypeError("new_fire_time must be an integer")
        self._last_fire_time = new_fire_time

    @property
    def name(self):
        """Return the name of the ship."""
        return self._name

    @property
    def make_time(self):
        """Return the time when the ship was created."""
        return self._initial_time

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
        """BallSprite in string form."""
        stringify = f"PaddleSrite({repr(self.position)}, "
        f"{repr(self.speed)}, {repr(self.width)}, {repr(self.height)}, "
        f'{repr(self._color)}, "{repr(self.position)}")'
        return stringify
    
def catmull_rom(p0, p1, p2, p3, t):
    t2, t3 = t*t, t*t*t
    return pygame.Vector2(
        0.5 * ((2*p1[0]) + (-p0[0] + p2[0]) * t + (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 + (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3),
        0.5 * ((2*p1[1]) + (-p0[1] + p2[1]) * t + (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 + (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)
    )