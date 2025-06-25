"""Game objects to create PyGame based games."""

import warnings
import pygame
from .scene import GalagaScene, MenuScene, GameOverScene
from .scenemanager import SceneManager

def display_info():
    """Print out information about the display driver and video information."""
    print(f'The display is using the "{pygame.display.get_driver()}" driver.')
    print("Video Info:")
    print(pygame.display.Info())


# If you're interested in using abstract base classes, feel free to rewrite
# these classes.
# For more information about Python Abstract Base classes, see
# https://docs.python.org/3.8/library/abc.html


# pylint: disable=too-few-public-methods
class VideoGame:
    """Base class for creating PyGame games."""

    def __init__(
        self,
        window_width=800,
        window_height=800,
        window_title="My Awesome Game",
    ):
        """Initialize a new game with the given window size and window title."""
        pygame.init()
        self._window_size = (window_width, window_height)
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(self._window_size)
        self._title = window_title
        pygame.display.set_caption(self._title)
        self._game_is_over = False
        if not pygame.font:
            warnings.warn("Fonts disabled.", RuntimeWarning)
        if not pygame.mixer:
            warnings.warn("Sound disabled.", RuntimeWarning)
        else:
            pygame.mixer.init()
        self._scene_manager = None

    def run(self):
        """Run the game; the main game loop."""
        raise NotImplementedError


# pylint: enable=too-few-public-methods

class Galaga(VideoGame):
    """This class holds the game Galaga."""
    def __init__(self):
        super().__init__(window_title = "Gino's Galaga")
        self._scene_manager = SceneManager(
            [MenuScene(self._screen)]
        )
        self._level = 1

    def run(self):
        current_scene = self._scene_manager._scenes[0]

        while current_scene.next_scene != "Quit":
            current_scene.begin_scene()

            while current_scene.is_valid():
                for event in pygame.event.get():
                    current_scene.process_event(event)
                current_scene.update_scene()
                current_scene.draw()
                pygame.display.flip()
                self._clock.tick(current_scene.frame_rate())

            current_scene.end_scene()
            match current_scene.next_scene:
                case "Continue Game":
                    current_scene = GalagaScene(self._screen, self._level, current_scene._score, current_scene._lives)
                    self._level += 1
                case "Menu":
                    current_scene = MenuScene(self._screen)
                case "GameOver":
                    current_scene = GameOverScene(self._screen, current_scene.score)
                case _:
                    break

    pygame.quit()