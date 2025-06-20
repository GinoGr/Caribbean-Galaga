"""Scene objects for making games with PyGame."""

import pygame
from videogame import rgbcolors
from videogame import assets
from videogame.ships import ShipSprite
from videogame.cannonball import CannonBallSprite

# If you're interested in using abstract base classes, feel free to rewrite
# these classes.
# For more information about Python Abstract Base classes, see
# https://docs.python.org/3.8/library/abc.html


class Scene:
    """Base class for making PyGame Scenes."""

    def __init__(
        self, screen, background_color, screen_flags=None, soundtrack=None
    ):
        """Scene initializer"""
        self._screen = screen
        if not screen_flags:
            screen_flags = pygame.SCALED
        #self._background = pygame.Surface(self._screen.get_size(), flags = screen_flags)
        self._background = pygame.image.load(assets.get('background')).convert()
        #self._background.fill(background_color)
        self._frame_rate = 60
        self._is_valid = True
        self._soundtrack = soundtrack
        self._render_updates = None

    def draw(self):
        """Draw the scene."""
        self._screen.blit(self._background, (0, 0))

    def process_event(self, event):
        """Process a game event by the scene."""
        if event.type == pygame.QUIT:
            print("Good Bye!")
            self._is_valid = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print("Bye bye!")
            self._is_valid = False

    def is_valid(self):
        """Is the scene valid? A valid scene can be used to play a scene."""
        return self._is_valid

    def render_updates(self):
        """Render all sprite updates."""

    def update_scene(self):
        """Update the scene state."""

    def start_scene(self):
        """Start the scene."""
        if self._soundtrack:
            try:
                pygame.mixer.music.load(self._soundtrack)
                pygame.mixer.music.set_volume(0.05)
            except pygame.error as pygame_error:
                print("\n".join(pygame_error.args))
                raise SystemExit("broken!!") from pygame_error
            pygame.mixer.music.play(loops=-1, fade_ms=500)

    def end_scene(self):
        """End the scene."""
        if self._soundtrack and pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(500)
            pygame.mixer.music.stop()

    def frame_rate(self):
        """Return the frame rate the scene desires."""
        return self._frame_rate


class PressAnyKeyToExitScene(Scene):
    """Empty scene where it will invalidate when a key is pressed."""

    def process_event(self, event):
        """Process game events."""
        super().process_event(event)
        if event.type == pygame.K_ESCAPE:
            self._is_valid = False

class GalagaScene(PressAnyKeyToExitScene):
    def __init__(self, screen):
        super().__init__(
            screen, rgbcolors.black, soundtrack = None
        )
    
        self._screen = screen

        (self.width, self.height) = self._screen.get_size()
        self._player_ship = ShipSprite(
            position = pygame.math.Vector2(self.width // 2, self.height - 50),
            direction = pygame.math.Vector2(0, 0),
            speed = 5,
            width = 50,
            height = 50,
            color = rgbcolors.white,
            name = "Player Ship"
        )
        self._sprites = pygame.sprite.Group(self._player_ship)
        
        self.last_fire_time = pygame.time.get_ticks()
        
    def draw(self):
        """Draw the scene."""
        super().draw()
        #self._screen.fill(rgbcolors.black)
        self._sprites.update()
        self._sprites.draw(self._screen)


    def begin_scene(self):
        """Begin the scene."""
        super().start_scene()

    def update_scene(self):
        self.player_action()

        # Move all cannonballs and remove those that are out of bounds
        for sprite in self._sprites:
            if isinstance(sprite, CannonBallSprite):
                sprite.move_ip(sprite.velocity.x, sprite.velocity.y)
                if sprite.rect.bottom < 0:
                    self._sprites.remove(sprite)
        return super().update_scene()
    
    def process_event(self, event):
        return super().process_event(event)
    
    def player_action(self):
        """Move the player ship in the given direction."""
        button = pygame.key.get_pressed()
        if(
            (button[pygame.K_LEFT] and button[pygame.K_RIGHT]) or 
            (button[pygame.K_a] and button[pygame.K_d])
        ):
            #do nothing if bot left and right pressed
            pass
        elif button[pygame.K_LEFT] or button[pygame.K_a]:
            if self._player_ship.rect.left > 0:
                self._player_ship.move_ip(-self._player_ship.speed, 0)
        elif button[pygame.K_RIGHT] or button[pygame.K_d]:
            if self._player_ship.rect.right < self.width:
                self._player_ship.move_ip(self._player_ship.speed, 0)
        if button[pygame.K_SPACE] or button[pygame.K_RETURN]:
            self.player_fire()
    def player_fire(self):
        """Fire a cannonball from the player ship."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time > 500:  # Fire every 1.5 seconds
            cannonball = CannonBallSprite(
                position = self._player_ship.position + pygame.math.Vector2(0, -self._player_ship.height // 2),
                direction = pygame.math.Vector2(0, -1),
                speed = 10,
                radius = 10,
                color = rgbcolors.black,
                name = "Cannon Ball"
            )
            self.last_fire_time = pygame.time.get_ticks()
            self._sprites.add(cannonball)

    def create_enemy(self):
        """Create an enemy ship at a random position."""
        enemy_ship = ShipSprite(
            position = pygame.math.Vector2(100, 100),
            direction = pygame.math.Vector2(1, 0),
            speed = 3,
            width = 50,
            height = 50,
            color = rgbcolors.red,
            name = "enemyship"
        )
        self._sprites.add(enemy_ship)

    def enemy_parametric_motion(self):
        for sprite in self._sprites:
            if isinstance(sprite, ShipSprite) and sprite.color == rgbcolors.red:
                t = pygame.time.get_ticks() - sprite._initial_time
                if t < 360:
                    x = 3 * pygame.math.sin(t)
                    y = 2 * pygame.math.cos(t)
                sprite.move_ip(x, y)