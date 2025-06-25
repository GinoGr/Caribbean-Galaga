"""Scene objects for making games with PyGame."""

import pygame
from videogame import rgbcolors
from videogame import assets
from videogame.ships import ShipSprite
from videogame.cannonball import CannonBallSprite
from videogame import highscores

# If you're interested in using abstract base classes, feel free to rewrite
# these classes.
# For more information about Python Abstract Base classes, see
# https://docs.python.org/3.8/library/abc.html


class Scene:
    """Base class for making PyGame Scenes."""

    def __init__(self, screen, screen_flags=None, soundtrack=None):
        """Scene initializer"""
        self._screen = screen
        if not screen_flags:
            screen_flags = pygame.SCALED
        # self._background = pygame.Surface(self._screen.get_size(), flags = screen_flags)
        self._background = pygame.image.load(assets.get("background")).convert()
        # self._background.fill(background_color)
        self._frame_rate = 60
        self._is_valid = True
        self._soundtrack = soundtrack
        self._render_updates = None
        self._next_scene = None

    @property
    def next_scene(self):
        """Returns which scene to show next"""
        return self._next_scene

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
    (-50, 250),
    (-50, 250),
    (150, 200),
    (200, 250),
    (150, 300),
    (50, 250),
    (250, 150),
    (-50, 150),
]
zig_zag_path = [
    (250, -100),
    (250, -100),
    (450, 100),
    (250, 200),
    (450, 300),
    (250, 400),
    (450, 500),
    (350, 300),
    (350, 300),
    (250, -100),
]


class GalagaScene(Scene):
    """Galaga Caribean Game Scene"""

    def __init__(self, screen, level=1, score=0, lives=2):
        super().__init__(screen, rgbcolors.black, soundtrack=None)
        """Initialize Game scene"""
        self._screen = screen

        (self.width, self.height) = self._screen.get_size()
        self._player_ship = ShipSprite(
            position=pygame.math.Vector2(self.width // 2, self.height - 50),
            direction=pygame.math.Vector2(0, 0),
            speed=5,
            width=50,
            height=50,
            name="Player Ship",
            rotate_angle=True,
            scale_factor=1 / 6,
        )
        self._ship_sprites = pygame.sprite.Group(self._player_ship)
        self._player_cannonball_sprites = pygame.sprite.Group()
        self._enemy_cannonball_sprites = pygame.sprite.Group()
        self._level_start = pygame.time.get_ticks()
        self._player_ship.last_fire_time = self._level_start
        self._last_enemy_spawn_time = self._level_start

        self._enemy_grid = self.generate_enemy_grid()
        self._grid_index = 0
        self._wave_index = 0
        self.wave_timer = self._level_start
        self._spawning_complete = False

        self._waves = [
            ("enemyship1", loop_path, -50, 250, "normal"),
            ("enemyship2", zig_zag_path, 850, 250, "normal"),
            ("enemyship3", loop_path, 850, 250, "reverse"),
            ("enemyship4", zig_zag_path, 850, 250, "reverse"),
        ]

        self._score = score
        self._lives = lives
        self._font = pygame.font.SysFont(None, 36)
        self._paused = False

        self._level = level

        self._show_level_text = True
        self._level_text_start_time = self._level_start

    @property
    def score(self):
        """Return score"""
        return self._score

    @property
    def lives(self):
        """Return number of lives left"""
        return self._lives

    def draw(self):
        """Draw the scene."""
        super().draw()
        # self._screen.fill(rgbcolors.black)
        self._ship_sprites.draw(self._screen)
        self._player_cannonball_sprites.draw(self._screen)
        self._enemy_cannonball_sprites.draw(self._screen)
        self.draw_scoreboard()
        if self._paused:
            paused_text = self._font.render("Respawning...", True, rgbcolors.red)
            self._screen.blit(paused_text, (self.width // 2 - 80, self.height // 2))

        if self._show_level_text:
            level_text = self._font.render(
                f"Level {self._level} Starting...", True, rgbcolors.red
            )
            self._screen.blit(level_text, (self.width // 2 - 100, self.height // 2))

    def draw_scoreboard(self):
        """Displays ui information"""
        score_text = self._font.render(f"Score: {self._score}", True, rgbcolors.red)
        lives_text = self._font.render(f"Lives: {self._lives}", True, rgbcolors.red)
        level_text = self._font.render(f"Level: {self._level}", True, rgbcolors.red)

        self._screen.blit(score_text, (10, 10))
        self._screen.blit(lives_text, (self.width // 2 - 60, 10))
        self._screen.blit(level_text, (650, 10))

    def begin_scene(self):
        """Begin the scene."""
        super().start_scene()

    def update_scene(self):
        """change next scene logic"""
        if self._show_level_text:
            if pygame.time.get_ticks() - self._level_text_start_time < 2000:
                return
            else:
                self._show_level_text = False
        elif self._paused:
            return
        delta_time = 1 / self._frame_rate
        self.player_action()
        self.enemy_fire()
        self._enemy_cannonball_sprites.update()
        self._player_cannonball_sprites.update()
        current_time = pygame.time.get_ticks()
        for sprite in self._ship_sprites:
            if getattr(sprite, "_is_exploading", False):
                if current_time - sprite._expload_start_time >= 500:
                    self._ship_sprites.remove(sprite)
            if sprite.name != "Player Ship":
                sprite.update_entry(delta_time)
                sprite.update_rush(delta_time)
        self._ship_sprites.update()

        self.cannonball_movement()
        self.detect_collisions()

        self.create_enemy_fleet()
        self.enemy_rush()

        if self.level_complete() and current_time - self._level_start > 32000:
            self._is_valid = False
            self._next_scene = "Continue Game"

        return super().update_scene()

    def process_event(self, event):
        """Process game quit or player death"""
        if event.type == pygame.USEREVENT + 1:
            self.respawn_player()
            self._paused = False
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        return super().process_event(event)

    def generate_enemy_grid(self):
        """Generate a grid of 8x4 positions and return as list of Vector2 positions."""
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

    def cannonball_movement(self):
        """Cannonballs move straight and disapear offscreen"""
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

                    enemy.expload("explosion")
                    self._player_cannonball_sprites.remove(cannonball)

        for cannonball in self._enemy_cannonball_sprites:
            if self._player_ship.hitbox.colliderect(cannonball.rect):
                self._player_ship.expload("explosion")
                self._lives -= 1

                if self._lives <= 0:
                    self._is_valid = False
                    self._next_scene = "GameOver"
                else:
                    self._paused = True
                    pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

        for enemy in self._ship_sprites:
            if enemy.name != "Player Ship":
                if self._player_ship.hitbox.colliderect(enemy.rect):
                    self._player_ship.expload("explosion")
                    enemy.expload("explosion")
                    self._lives -= 1
                    if self._lives <= 0:
                        self._is_valid = False
                        self._next_scene = "GameOver"
                    else:
                        self._paused = True
                        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

    def player_action(self):
        """Move the player ship in the given direction."""
        button = pygame.key.get_pressed()
        if (button[pygame.K_LEFT] and button[pygame.K_RIGHT]) or (
            button[pygame.K_a] and button[pygame.K_d]
        ):
            # do nothing if button left and right pressed
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
        if (
            current_time - self._player_ship.last_fire_time > 500
        ):  # Fire every 0.5 seconds
            cannonball = CannonBallSprite(
                position=self._player_ship.position
                + pygame.math.Vector2(0, -self._player_ship.height // 2),
                direction=pygame.math.Vector2(0, -1),
                speed=10,
                radius=10,
                color=rgbcolors.black,
                name="Player Cannon Ball",
            )
            self._player_ship.last_fire_time = pygame.time.get_ticks()
            self._player_cannonball_sprites.add(cannonball)

    def respawn_player(self):
        """Reset player ship after death"""
        self._player_ship = ShipSprite(
            position=pygame.math.Vector2(self.width // 2, self.height - 50),
            direction=pygame.math.Vector2(0, 0),
            speed=5,
            width=50,
            height=50,
            name="Player Ship",
            rotate_angle=True,
            scale_factor=1 / 6,
        )
        self._ship_sprites.add(self._player_ship)
        self._player_ship.last_fire_time = pygame.time.get_ticks()

    def enemy_fire(self):
        """Fire a cannonball from the enemy ships."""
        current_time = pygame.time.get_ticks()
        for enemy in self._ship_sprites:
            if (
                enemy.name != "Player Ship"
                and current_time - enemy.last_fire_time - enemy.make_time
                > enemy.fire_every
            ):
                cannonball = CannonBallSprite(
                    position=enemy.position + pygame.math.Vector2(0, enemy.height // 2),
                    direction=pygame.math.Vector2(0, 1),
                    speed=9 + self._level,
                    radius=10,
                    color=rgbcolors.black,
                    name="Enemy Cannon Ball",
                )
                enemy.last_fire_time = pygame.time.get_ticks()
                self._enemy_cannonball_sprites.add(cannonball)

    def enemy_rush(self):
        """Fire a cannonball from the enemy ships."""
        current_time = pygame.time.get_ticks()
        for enemy in self._ship_sprites:
            if (
                not enemy.name == "Player Ship"
                and current_time - enemy.last_time_rush - enemy.make_time
                > enemy.rush_every
            ):
                enemy.enable_rushing_path()

                enemy.last_time_rush = pygame.time.get_ticks()

    def create_enemy_fleet(self):
        """Spawns all enemies neccessary for each level"""
        if self._wave_index >= len(self._waves):
            self._spawning_complete = True
            return

        current_time = pygame.time.get_ticks()
        if current_time - self._last_enemy_spawn_time < 500:
            return

        self._last_enemy_spawn_time = current_time
        image, path, x, y, mode = self._waves[self._wave_index]

        if self._grid_index >= len(self._enemy_grid):
            self._spawning_complete = True
            return

        enemy = ShipSprite(
            position=pygame.math.Vector2(x, y),
            direction=pygame.math.Vector2(0, 0),
            speed=0,
            width=100 if "4" in image else 200,
            height=100 if "4" in image else 150,
            name=image,
            image_path=image,
            path=path,
            grid=self._enemy_grid[self._grid_index],
            level=self._level,
        )
        if mode == "reverse":
            enemy.reverse_entry_direction()

        enemy.enable_entry_path()
        self._ship_sprites.add(enemy)
        self._grid_index += 1

        if self._grid_index % 8 == 0:
            self._wave_index += 1

    def level_complete(self):
        """Checks to see if the player ship is the only sprite in the ship sprites"""
        return all(sprite.name == "Player Ship" for sprite in self._ship_sprites)


class MenuScene(Scene):
    """Menu and rules are displayed here."""

    def __init__(self, screen):
        """Initialize menu scene"""
        super().__init__(screen, rgbcolors.black)

        self._screen = screen

        (self.width, self.height) = self._screen.get_size()

        self._score = 0
        self._lives = 2

    @property
    def score(self):
        """Return begining score"""
        return self._score

    @property
    def lives(self):
        """Returns game start number of lives"""
        return self._lives

    def process_event(self, event):
        """Catch is player wants to quit"""
        super().process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
            self._is_valid = False
            self._next_scene = "Continue Game"

    def begin_scene(self):
        """First step in new scene"""
        self.start_scene()

    def draw(self):
        """Draw rules to menu screen"""
        super().draw()
        title_font = pygame.font.Font(None, 60)
        subtitle_font = pygame.font.Font(None, 40)
        text_font = pygame.font.Font(None, 30)

        title_text = title_font.render("Galaga:", True, rgbcolors.white)
        title_text_pos = title_text.get_rect(
            center=(self.width / 2, title_font.get_linesize() * 2)
        )
        self._background.blit(title_text, title_text_pos)

        sub_title_text = subtitle_font.render("In The Caribbean", True, rgbcolors.white)
        sub_title_text_pos = sub_title_text.get_rect(
            center=(self.width / 2, (title_font.get_linesize() * 2) + 50)
        )
        self._background.blit(sub_title_text, sub_title_text_pos)

        rules_text = (
            "Game Rules:\nUp Arrow/W: Move paddle up\nDown Arrow/S: move paddle down"
        )

        y_offset = 175
        rules_text = "By Gino Grandin\n"
        rules_text += (
            "In this game, you are a pirate trying to kill the pursuing ships\n"
        )

        rules_text += "Your goal in this game is to get to the highest score you can\n"
        rules_text += "To get points, you must shoot the enemy ships\n"
        rules_text += "Use 'a' or the left key to move left\n"
        rules_text += "Use 'd' or the right key to move right\n"
        rules_text += "Use the space or the enter key to shoot your ship's cannon\n"
        rules_text += "The enemy ships will randomly shoot and rush you. Avoid both.\n"
        rules_text += "Complete a level by sinking all enemy ships\n"
        rules_text += "As levels progress, the game will get harder\n"
        rules_text += "Try your best and have fun!"
        rule_lines = rules_text.split("\n")

        font = pygame.font.Font(None, 30)
        for line in rule_lines:
            game_rules = font.render(line, True, rgbcolors.white)
            game_rules_pos = game_rules.get_rect(center=(self.width / 2, y_offset))
            self._background.blit(game_rules, game_rules_pos)
            y_offset += font.get_linesize() * 2

        y_offset += 100
        rules_text = "Press any botton to continue or esc key to quit"

        font = pygame.font.Font(None, 30)
        game_rules = font.render(rules_text, True, rgbcolors.white)
        game_rules_pos = game_rules.get_rect(center=(self.width / 2, y_offset))
        self._background.blit(game_rules, game_rules_pos)
        y_offset += font.get_linesize() * 2


class GameOverScene(Scene):
    def __init__(self, screen, score):
        """Initalize game over/scoreboard scene"""
        super().__init__(screen)
        self._next_scene = "Menu"
        self._score = score
        self._font = pygame.font.Font(None, 50)
        self._name = ""
        self._entered = False

    def begin_scene(self):
        """First step in new scene"""
        self.start_scene()

    def process_event(self, event):
        """Allows for input for new high scores"""
        super().process_event(event)
        if event.type == pygame.KEYDOWN:
            if not self._entered:
                if event.key == pygame.K_BACKSPACE:
                    self._name = self._name[:-1]
                elif event.key == pygame.K_RETURN and len(self._name) == 3:
                    from videogame import highscores

                    highscores.add_score(self._name.upper(), self._score)
                    self._entered = True
                elif len(self._name) < 3 and event.unicode.isalpha():
                    self._name += event.unicode.upper()
            else:
                self._is_valid = False
                self._next_scene = "Menu"

    def draw(self):
        """Draws highscores to screen"""
        super().draw()
        if not self._entered:
            msg = self._font.render(
                f"GAME OVER - SCORE: {self._score}", True, rgbcolors.white
            )
            prompt = self._font.render(
                f"Enter 3-char Name: {self._name}", True, rgbcolors.red
            )
            self._screen.blit(msg, (200, 200))
            self._screen.blit(prompt, (200, 250))
        else:
            scores = highscores.load_highscores()
            self._screen.blit(
                self._font.render("HIGH SCORES:", True, rgbcolors.white), (200, 200)
            )
            for i, (name, score) in enumerate(scores):
                line = self._font.render(
                    f"{i+1}. {name} - {score}", True, rgbcolors.red
                )
                self._screen.blit(line, (200, 250 + i * 40))
