"""
"""

import arcade
import random
import itertools
import pymunk

from enum import Enum
from loguru import logger

from .map import DungeonMap


class DungeonWindow(arcade.Window):
    def __init__(self, width: int, height: int, num_rooms: int):

        super().__init__(width, height)

        arcade.set_background_color((0x9B, 0x76, 0x53, 255))

        self.num_rooms = num_rooms

        for _ in range(num_rooms):
            self.map.add_room()

        self.paused = True

        self.release_actions = {
            arcade.key.ESCAPE: quit,
            arcade.key.SPACE: self.toggle_pause,
            arcade.key.B: self.begin,
            arcade.key.R: self.reset,
        }

    @property
    def map(self):
        try:
            return self._map
        except AttributeError:
            pass

        self._map = DungeonMap(self.width, self.height)

        return self._map

    @property
    def center(self) -> tuple:
        try:
            return self._center
        except AttributeError:
            pass
        self._center = (self.width // 2, self.height // 2)
        return self._center

    def begin(self):
        """
        """
        logger.info("DW begin")

    def toggle_pause(self):
        """
        """

        self.paused = not self.paused
        logger.info(f"Paused: {self.paused}")

    def reset(self):

        logger.info("DW reset")

        self.paused = True

        self.map.reset()

    def setup(self):
        """
        """

        logger.info(f"setup: rooms={self.num_rooms}")

        self.map.setup()
        self.map.advance()

    def on_key_release(self, key, modifier):

        try:
            f = self.release_actions[key]
            f()
        except KeyError:
            pass

    def on_update(self, dt: float):

        if self.paused:
            return

        self.map.update()

    def on_draw(self):

        arcade.start_render()
        self.map.draw()

        arcade.draw_text(
            f"{self.map.mode!r} {self.map.space.current_time_step}",
            20,
            20,
            arcade.color.WHITE,
            14,
        )
