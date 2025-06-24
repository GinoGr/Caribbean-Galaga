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

loop_path = [
            (-50, 250),(-50, 250), (150, 200), (200, 250), (150, 300), (50, 250), (250, 150), (-50, 150)
        ]
zig_zag_path = [
            (250, -100), (250, -100), (450, 100),
            (250, 200), (450, 300), (250, 400), (450, 500), (350, 300),
            (350, 300), (250, -100)
        ]

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
            name = "Player Ship",
            rotate_angle = True,
            scale_factor = 1 / 6
        )
        self._ship_sprites = pygame.sprite.Group(self._player_ship)
        self._player_cannonball_sprites = pygame.sprite.Group()
        self._enemy_cannonball_sprites = pygame.sprite.Group()
        self._player_ship.last_fire_time = pygame.time.get_ticks()
        self._last_enemy_spawn_time = pygame.time.get_ticks()

        self._enemy_grid = self.generate_enemy_grid()

        self._grid_index = 0

        self._score = 0
        self._lives = 2
        self._font = pygame.font.SysFont(None, 36)
        self._paused = False

    def draw(self):
        """Draw the scene."""
        super().draw()
        #self._screen.fill(rgbcolors.black)
        self._ship_sprites.draw(self._screen)
        self._player_cannonball_sprites.draw(self._screen)
        self._enemy_cannonball_sprites.draw(self._screen)
        self.draw_scoreboard()
        if self._paused:
            paused_text = self._font.render("Respawning...", True, rgbcolors.red)
            self._screen.blit(paused_text, (self.width // 2 - 80, self.height // 2))

        for pos in self._enemy_grid:
            pygame.draw.circle(self._screen, rgbcolors.red, (int(pos.x), int(pos.y)), 4)

    def draw_scoreboard(self):
        score_text = self._font.render(f"Score: {self._score}", True, rgbcolors.red)
        lives_text = self._font.render(f"Lives: {self._lives}", True, rgbcolors.red)

        self._screen.blit(score_text, (10, 10))
        self._screen.blit(lives_text, (10, 50))


    def begin_scene(self):
        """Begin the scene."""
        super().start_scene()

    def update_scene(self):
        if self._paused:
            return
        delta_time = 1 / self._frame_rate
        self.player_action()
        self.enemy_fire()
        self._enemy_cannonball_sprites.update()
        self._player_cannonball_sprites.update()
        current_time = pygame.time.get_ticks()
        for sprite in self._ship_sprites:
            if getattr(sprite, '_is_exploading', False):
                if current_time - sprite._expload_start_time >= 500:
                    self._ship_sprites.remove(sprite)
            if sprite.name != "Player Ship" :
                sprite.update_entry(delta_time)
                sprite.update_rush(delta_time)
        self._ship_sprites.update()

        self.cannonball_movement()
        self.detect_collisions()
    
        self.create_enemy_fleet()
        self.enemy_rush()
        
        return super().update_scene()
    
    def process_event(self, event):
        if event.type == pygame.USEREVENT + 1:
            self.respawn_player()
            self._paused = False
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        return super().process_event(event)
    
    def cannonball_movement(self):
        for sprite in self._player_cannonball_sprites:
            sprite.move_ip(sprite.velocity.x, sprite.velocity.y)
            if sprite.rect.bottom < 0:
                self._player_cannonball_sprites.remove(sprite)

        for sprite in self._enemy_cannonball_sprites:
            sprite.move_ip(sprite.velocity.x, sprite.velocity.y)
            if sprite.rect.top > self.height:
                self._enemy_cannonball_sprites.remove(sprite)

    def detect_collisions(self):
        """Detect collisions between player cannonballs and enemy ships."""
        for sprite in self._ship_sprites:
            sprite.hitbox.center = sprite.rect.center
        for cannonball in self._player_cannonball_sprites:
            # Check for collisions with player cannonballs
            hit_enemies = []
            for s in self._ship_sprites:
                if s.name == "Player Ship":
                    continue
                if s.hitbox.colliderect(cannonball.rect):
                    hit_enemies.append(s)
        
            if hit_enemies:
                for enemy in hit_enemies:
                    if enemy._state == "idle":
                        self._score += 50
                    else:
                        self._score += 100

                    if self._score // 10000 > (self._score - 100) // 10000:
                        self._lives += 1

                    enemy.expload('explosion')
                    self._player_cannonball_sprites.remove(cannonball)
        
        for cannonball in self._enemy_cannonball_sprites:
                if self._player_ship.hitbox.colliderect(cannonball.rect):
                    self._player_ship.expload('explosion')
                    self._lives -= 1

                    if self._lives <= 0:
                        self._is_valid = False
                    else:
                        self._paused = True
                        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

        for enemy in self._ship_sprites:
                if enemy.name != "Player Ship":
                    if self._player_ship.hitbox.colliderect(enemy.rect):
                        self._player_ship.expload('explosion')
                        enemy.expload('explosion')
                        self._lives -= 1
                        if self._lives <= 0:
                            self._is_valid = False
                        else:
                            self._paused = True
                            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

    def player_action(self):
        """Move the player ship in the given direction."""
        button = pygame.key.get_pressed()
        if(
            (button[pygame.K_LEFT] and button[pygame.K_RIGHT]) or 
            (button[pygame.K_a] and button[pygame.K_d])
        ):
            #do nothing if button left and right pressed
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
        if current_time - self._player_ship.last_fire_time > 500:  # Fire every 0.5 seconds
            cannonball = CannonBallSprite(
                position = self._player_ship.position + pygame.math.Vector2(0, -self._player_ship.height // 2),
                direction = pygame.math.Vector2(0, -1),
                speed = 10,
                radius = 10,
                color = rgbcolors.black,
                name = "Player Cannon Ball"
            )
            self._player_ship.last_fire_time = pygame.time.get_ticks()
            self._player_cannonball_sprites.add(cannonball)

    def enemy_fire(self):
        """Fire a cannonball from the enemy ships."""
        current_time = pygame.time.get_ticks()
        for enemy in self._ship_sprites:
            if(
                enemy.name != "Player Ship" and 
                current_time - enemy.last_fire_time > enemy.fire_every
            ):
                cannonball = CannonBallSprite(
                    position = enemy.position + pygame.math.Vector2(0, enemy.height // 2),
                    direction = pygame.math.Vector2(0, 1),
                    speed = 10,
                    radius = 10,
                    color = rgbcolors.black,
                    name = "Enemy Cannon Ball"
                )
                enemy.last_fire_time = pygame.time.get_ticks()
                self._enemy_cannonball_sprites.add(cannonball)

    def enemy_rush(self):
        """Fire a cannonball from the enemy ships."""
        current_time = pygame.time.get_ticks()
        for enemy in self._ship_sprites:
            if(
                not enemy.name == "Player Ship" and 
                current_time - enemy.last_time_rush > enemy.rush_every
            ):
                enemy.enable_rushing_path()

                enemy.last_time_rush = pygame.time.get_ticks()

    def create_enemy_fleet(self):
        if 9001 > pygame.time.get_ticks() > 5000:
            if pygame.time.get_ticks() - self._last_enemy_spawn_time > 500:
                self._last_enemy_spawn_time = pygame.time.get_ticks()
                enemy = ShipSprite(
                    position = pygame.math.Vector2(-50, 250),
                    direction = pygame.math.Vector2(0, 0),
                    speed = 0,
                    width = 200,
                    height = 150,
                    name = "enemyship",
                    image_path = "enemyship1",
                    path = loop_path,
                    grid = (self._enemy_grid[self._grid_index])
                )
                # Create path ending at grid spot
                enemy.enable_entry_path()
                self._ship_sprites.add(enemy)
                self._grid_index = self._grid_index + 1
        elif 16001 > pygame.time.get_ticks() > 12000:
            if pygame.time.get_ticks() - self._last_enemy_spawn_time > 500:
                self._last_enemy_spawn_time = pygame.time.get_ticks()
                enemy = ShipSprite(
                    position = pygame.math.Vector2(850, 250),
                    direction = pygame.math.Vector2(0, 0),
                    speed = 0,
                    width = 200,
                    height = 150,
                    name = "enemyship2",
                    image_path = "enemyship2",
                    path = zig_zag_path,
                    grid = (self._enemy_grid[self._grid_index])
                )
                # Create path ending at grid spot
                enemy.enable_entry_path()
                self._ship_sprites.add(enemy)
                self._grid_index += 1
        elif 22001 > pygame.time.get_ticks() > 18000:
            if pygame.time.get_ticks() - self._last_enemy_spawn_time > 500:
                self._last_enemy_spawn_time = pygame.time.get_ticks()
                enemy = ShipSprite(
                    position = pygame.math.Vector2(850, 250),
                    direction = pygame.math.Vector2(0, 0),
                    speed = 0,
                    width = 200,
                    height = 150,
                    name = "enemyship3",
                    image_path = "enemyship3",
                    path = loop_path,
                    grid = (self._enemy_grid[self._grid_index])
                )
                # Create path ending at grid spot
                enemy.reverse_entry_direction()
                enemy.enable_entry_path()
                self._ship_sprites.add(enemy)
                self._grid_index += 1
        elif 32001 > pygame.time.get_ticks() > 28000:
            if pygame.time.get_ticks() - self._last_enemy_spawn_time > 500:
                self._last_enemy_spawn_time = pygame.time.get_ticks()
                enemy = ShipSprite(
                    position = pygame.math.Vector2(850, 250),
                    direction = pygame.math.Vector2(0, 0),
                    speed = 0,
                    width = 100,
                    height = 100,
                    name = "enemyship4",
                    image_path = "enemyship4",
                    path = zig_zag_path,
                    grid = (self._enemy_grid[self._grid_index])
                )
                # Create path ending at grid spot
                enemy.reverse_entry_direction()
                enemy.enable_entry_path()
                self._ship_sprites.add(enemy)
                self._grid_index += 1

    def respawn_player(self):
        self._player_ship = ShipSprite(
            position = pygame.math.Vector2(self.width // 2, self.height - 50),
            direction = pygame.math.Vector2(0, 0),
            speed = 5,
            width = 50,
            height = 50,
            name = "Player Ship",
            rotate_angle = True,
            scale_factor = 1 / 6
        )
        self._ship_sprites.add(self._player_ship)
        self._player_ship.last_fire_time = pygame.time.get_ticks()

    def generate_enemy_grid(self):
        """Generate a grid of 8x4 positions and return as list of Vector2s."""
        cols = 8
        rows = 4
        spacing_x = 90
        spacing_y = 120
        top_margin = 75
        left_margin = (self.width - (cols - 1) * spacing_x) // 2
        grid = []
        for row in range(rows):
            for col in range(cols):
                x = left_margin + col * spacing_x
                y = top_margin + row * spacing_y
                grid.append(pygame.Vector2(x, y))
        return grid