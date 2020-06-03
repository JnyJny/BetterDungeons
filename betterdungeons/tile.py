"""
"""

import arcade

import math
import pymunk
import random

from loguru import logger
from pathlib import Path
from PIL import Image, ImageDraw

from .resources import path_for
from .sprite import PhysicsSprite

ROOM = 1
WALL = 2


class RoomSprite(PhysicsSprite):

    collision_type = ROOM

    _margin = 0

    @classmethod
    def random_sizes(cls, x: int, y: int, min_dim: int = 1, max_dim: int = 10):
        w = random.randint(min_dim, max_dim)
        h = random.randint(min_dim, max_dim)

        return cls(x, y, w, h)

    def __init__(self, x, y, w, h, grid: int = 10):

        super().__init__()

        self.wall = 4
        self.grid = grid + 1
        self.width = (w * grid) + (w - 1) + (self.wall * 2)
        self.height = (h * grid) + (h - 1) + (self.wall * 2)
        self.set_position(x, y)

        self.texture = self.grid_texture
        self._points = self.texture.hit_box_points

        self.shape.friction = 0.9
        self.shape.elasticity = 1.0
        self.shape.density = 0.5
        self.shape.collision_type = self.collision_type

        self.touching = 0
        logger.info(str(self))

    def set_position(self, center_x: float, center_y: float):
        super().set_position(center_x, center_y)
        self.body.position = pymunk.Vec2d(center_x, center_y)

    @property
    def grid_texture(self):

        try:
            return self._grid_texture
        except AttributeError:
            pass

        img = Image.new("RGBA", (self.width, self.height), (255, 255, 255, 255))

        self._grid_texture = arcade.Texture(f"RGBA-grid-{id(self)}", img)

        fill = (255, 0, 0, 255)

        draw = ImageDraw.Draw(img)

        w = self.width
        h = self.height

        for x in range(self.grid + self.wall, w, self.grid):
            hline = ((x, 0), (x, h))
            draw.line(hline, fill=fill, width=1)

        for y in range(self.grid + self.wall, h, self.grid):
            vline = ((0, y), (w, y))
            draw.line(vline, fill=fill)

        draw.rectangle(((0, 0), (w, h)), outline=(0, 0, 0, 255), width=self.wall)

        return self._grid_texture

    @property
    def center(self):
        return self.body.position

    def __str__(self):
        size = f"{self.width}x{self.height}"
        velocity = f"{self.body.velocity.get_length():.2f}"
        return f"Sprite @ {self.center} {size}"

    def update(self):

        if not self.body.is_sleeping:

            if self.touching:
                self.color = (255, 0, 0, 64)
                self.shape.friction = 0
            else:
                self.color = (255, 255, 255, 255)
                self.shape.friction = 1

    def draw(self):
        logger.info("draw")


class WallSprite(arcade.SpriteSolidColor):

    collision_type = WALL

    def __str__(self):

        return f"Wall {self.width}x{self.height} {self.body.position}"

    def set_position(self, center_x: float, center_y: float):
        super().set_position(center_x, center_y)
        self.body.position = pymunk.Vec2d(center_x, center_y)

    @property
    def body(self):
        try:
            return self._body
        except AttributeError:
            pass

        self._body = pymunk.Body(1, 0, pymunk.Body.STATIC)

        return self._body

    @property
    def shape(self):
        try:
            return self._shape
        except AttributeError:
            pass

        self._shape = pymunk.Poly.create_box(self.body, (self.width, self.height))

        self._shape.collision_type = self.collision_type

        return self._shape

    def draw(self):
        logger.info("wall draw")
        self.color = (255, 0, 0, 255) if self.colliding else (0, 255, 0, 255)
