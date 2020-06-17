"""
"""


import arcade
import itertools
import pymunk

import numpy as np

from enum import Enum, auto
from loguru import logger
from scipy.spatial import Delaunay

from .physics_sprite import PhysicsSpriteList
from .sprites import RoomSprite, WallSprite


class MapMode(int, Enum):
    Ready = 0
    Colliding = 1
    Adjusting = 2
    Culling = 3
    Neighbors = 4
    Done = 5

    # def __iter__(self):
    #    return self

    def __next__(self):
        try:
            return self.__class__(self.value + 1)
        except ValueError:
            return self.__class__(5)


class DungeonMap:
    """
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.quiesced = False
        self.mode = MapMode.Ready
        self.culled = False
        self.can_draw_neighbors = False

    @property
    def space(self):
        try:
            return self._space
        except AttributeError:
            pass

        self._space = pymunk.Space()
        self._space.iterations = 30
        self._space.collision_bias = 0.01
        # self._space.collision_slop = 0.1
        self._space.damping = 0.9
        # self._space.sleep_time_threshold = 1
        # self._space.idle_speed_threshold = 5

        return self._space

    @property
    def center(self) -> tuple:
        """Center coordinates of the map: (x,y).
        """
        try:
            return self._center
        except AttributeError:
            pass

        self._center = (self.width // 2, self.height // 2)

        return self._center

    @property
    def bounds(self) -> PhysicsSpriteList:
        """List of static bounds around the map.
        """
        try:
            return self._bounds
        except AttributeError:
            pass

        self._bounds = PhysicsSpriteList(space=self.space)

        w = 3
        c = (0, 255, 0, 255)

        cx, cy = self.center

        top = WallSprite(self.width, w, c)
        top.set_position(cx, 0)

        bottom = WallSprite(self.width, w, c)
        bottom.set_position(cx, self.height)

        left = WallSprite(w, self.height, c)
        left.set_position(0, cy)

        right = WallSprite(w, self.height, c)
        right.set_position(self.width, cy)

        for bound in [top, bottom, left, right]:
            self._bounds.append(bound)

        return self._bounds

    @property
    def rooms(self) -> PhysicsSpriteList:
        """List of dynamic rooms in the map.
        """
        try:
            return self._rooms
        except AttributeError:
            pass

        self._rooms = PhysicsSpriteList(space=self.space)

        return self._rooms

    @property
    def triangles(self) -> list:

        try:

            return self._triangles
        except AttributeError:
            pass

        if self.mode < MapMode.Neighbors:
            return []

        points = np.array([r.position for r in self.rooms])

        tri = Delaunay(points)

        logger.info(f"points: {points}")
        logger.info(f"simplices: {tri.simplices}")

        self._triangles = points[tri.simplices].tolist()

        for tri in self._triangles:
            tri.append(tri[0])

        return self._triangles

    @property
    def nudge(self) -> pymunk.Vec2d:
        """A cyclic force vector.
        """
        try:
            return next(self._nudge)
        except AttributeError:
            pass

        f = max(self.width // 4, self.height // 4)

        forces = [
            pymunk.Vec2d(*v)
            for v in itertools.combinations_with_replacement([0, f, f // 2], 2)
        ]

        self._nudge = itertools.cycle(forces)

        return next(self._nudge)

    def add_room(self, position: tuple = None) -> None:
        """Add a room to the map at `position`, self.center by default.
        """
        position = position or self.center

        room = RoomSprite.random_size(space=self.space)

        room.set_position(*position)

        self.rooms.append(room)

    def reset(self) -> None:
        """Reset the map to start.
        """
        for room in self.rooms:
            room.set_position(*self.center)
            self.space.reindex_shapes_for_body(room.body)

    def setup(self) -> None:
        """
        """
        for room in self.rooms:
            room.body.apply_impulse_at_local_point(self.nudge, room.center)
            logger.info(room)

    def advance(self) -> None:
        """
        """
        logger.info(f"Advancing map mode from {self.mode!r} to {next(self.mode)!r}")
        self.mode = next(self.mode)

    @property
    def update_map(self):
        try:
            return self._update_map
        except AttributeError:
            pass

        self._update_map = {
            MapMode.Colliding: self.update_colliding,
            MapMode.Adjusting: self.update_adjusting,
            MapMode.Culling: self.update_culling,
            MapMode.Neighbors: self.update_neighbors,
            MapMode.Done: self.update_done,
        }

        return self._update_map

    def update(self):

        try:
            self.update_map[self.mode]()
        except KeyError:
            logger.warning(f"Missing update for {self.mode}")

    def update_colliding(self):
        """
        """

        for _ in range(10):
            self.space.step(0.01)

        self.rooms.update()

        v = 0
        for room in self.rooms:
            touching = arcade.check_for_collision_with_list(room, self.rooms)
            room.touching = len(touching)
            if room.touching:
                room.body.apply_impulse_at_local_point(self.nudge // 2, room.center)
            v += room.body.velocity.length

        if v < 1.0:
            self.advance()

    def update_adjusting(self):

        # for room in self.rooms:
        #    x, y = room.position
        #    x -= x % 10
        #    y -= y % 10
        #    room.set_position(x + 10, y + 10)

        self.advance()

    def update_culling(self):

        # n = max(int(len(self.rooms) * 0.75), 3)
        #
        # smallest = sorted(self.rooms, key=lambda v: v.width * v.height)[:n]
        # for room in smallest:
        #    self.rooms.remove(room)

        self.advance()

    def update_neighbors(self):

        triangulation = Delaunay(np.array([r.position for r in self.rooms]))

        for tri in triangulation.simplices:
            neighbors = [self.rooms[n] for n in tri]
            for neighbor in neighbors:
                neighbor.neighbors.extend(set(neighbors) - {neighbor})

        self.advance()

    def update_done(self):

        pass

    def draw(self):
        """
        """
        self.bounds.draw()
        self.rooms.draw()

        for room in self.rooms:
            for hallway in room.hallways:
                hallway.draw()
