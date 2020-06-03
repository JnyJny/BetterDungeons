"""
"""

import arcade
import pymunk


class PhysicsSpriteList(arcade.SpriteList):
    def __init__(self, *args, **kwds):
        self.space = kwds["space"]
        del kwds["space"]
        super().__init__(args, **kwds)

    def append(self, sprite) -> None:
        """
        """
        super().append(sprite)
        self.space.add(sprite.body, sprite.shape)

    def remove(self, sprite) -> None:
        """
        """

        super().remove(sprite)
        self.space.remove(sprite.body, sprite.shape)


class PhysicsSprite(arcade.Sprite):
    """
    """

    def __init__(self, *args, **kwds):

        self.body_type = kwds.get("body_type", pymunk.Body.DYNAMIC)
        self.space = kwds.get("space", None)

        for key in ["body_type", "space"]:
            try:
                del kwds[key]
            except Exception:
                pass
        super().__init__(*args, **kwds)

    def set_position(self, x: float, y: float):

        super().set_position(x, y)
        self.body.position = pymunk.Vec2d(x, y)

    @property
    def shape(self):
        try:
            return self._shape
        except AttributeError:
            pass

        self._shape = pymunk.Poly.create_box(self.body, (self.width, self.height))

        return self._shape

    @property
    def body(self):
        try:
            return self._body
        except AttributeError:
            pass

        self._body = pymunk.Body(0, 0, self.body_type)

        return self._body

    def sync(self):
        """
        """
        self.center_x, self.center_y = self.body.position

    def update(self):
        self.sync()
