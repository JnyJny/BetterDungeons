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
from .physics_sprite import PhysicsSprite

ROOM = 1
WALL = 2


class RoomSprite(PhysicsSprite):

    _margin = 0

    @classmethod
    def random_size(cls, space: pymunk.Space, min_dim: int = 1, max_dim: int = 10):

        w = random.randint(min_dim, max_dim)
        h = random.randint(min_dim, max_dim)

        return cls(w, h, space=space)

    def __init__(
        self, width: float, height: float, space: pymunk.Space, grid: int = 10, **kwds
    ):

        super().__init__(space=space)

        self.wall = 3
        self.line = 1
        self.grid = grid
        self.grid_x = width
        self.grid_y = height

        self.width = (self.wall * 2) + (self.grid * width) + (self.line * (width - 1))
        self.height = (
            (self.wall * 2) + (self.grid * height) + (self.line * (height - 1))
        )

        self.append_texture(self.gridtexture)
        self.set_texture(0)

        self.shape.friction = 0.9
        self.shape.elasticity = 1.0
        self.shape.density = 0.5

        self.touching = 0

    def set_position(self, center_x: float, center_y: float):
        super().set_position(center_x, center_y)
        self.body.position = pymunk.Vec2d(center_x, center_y)

    def __hash__(self):
        return id(self)

    @property
    def gridtexture(self):

        try:
            return self._grid
        except AttributeError:
            pass

        img = Image.new("RGBA", (self.width, self.height), (255, 255, 255, 255))

        self._gridtexture = arcade.Texture(f"RGBA-grid-{id(self)}", img)

        fill = (255, 0, 0, 255)

        draw = ImageDraw.Draw(img)

        w = self.width
        h = self.height

        for dx in range(1, self.grid_x):
            x = self.wall + (dx * self.grid) + (dx * self.line)
            hline = ((x, 0), (x, h))
            draw.line(hline, fill=fill, width=self.line)

        for dy in range(1, self.grid_y):
            y = self.wall + (dy * self.grid) + (dy * self.line)
            vline = ((0, y), (w, y))
            draw.line(vline, fill=fill, width=self.line)

        draw.rectangle(((0, 0), (w, h)), outline=(0, 0, 0, 255), width=self.wall)

        self._points = self._gridtexture.hit_box_points

        return self._gridtexture

    @property
    def center(self):
        return self.body.position

    def __str__(self):
        size = f"{self.width}x{self.height}"
        velocity = f"{self.body.velocity.get_length():.2f}"
        return f"Sprite @ {self.center} {size}"

    @property
    def neighbors(self):
        try:
            return self._neighbors
        except AttributeError:
            pass
        self._neighbors = []
        return self._neighbors

    @property
    def hallways(self):
        try:
            if len(self.neighbors) == 0:
                return []
            return self._hallways
        except AttributeError:
            pass
        self._hallways = []

        for neighbor in self.neighbors:
            A = pymunk.Vec2d(*self.position)
            B = pymunk.Vec2d(*neighbor.position)
            C = (A + B) / 2
            w, h = A - B
            shape = arcade.create_rectangle_outline(*C, w, h, (0, 127, 0, 127), 1)
            self._hallways.append(shape)

        return self._hallways

    def update(self):

        super().update()

        if self.touching:
            self.color = (255, 0, 0, 64)
            self.shape.friction = 0
        else:
            self.color = (255, 255, 255, 255)
            self.shape.friction = 1

    def on_draw(self, dt: float):
        super().on_draw(dt)
        for hallway in self.hallways:
            hallway.draw()


class WallSprite(PhysicsSprite):
    def __init__(self, *args, **kwds):

        kwds["body_type"] = pymunk.Body.STATIC

        super().__init__(*(), **kwds)
        self.width, self.height, self.color = args

        img = Image.new("RGBA", (self.width, self.height), self.color)
        self.texture = arcade.Texture(f"RGBA-{self.__class__.__name__}-{id(self)}", img)

    def __str__(self):

        return f"Wall {self.width}x{self.height} {self.body.position}"
