"""
"""

import typer
import arcade

from .dungeon import DungeonWindow

cli = typer.Typer()


@cli.command()
def start(
    width: int = typer.Option(1024, "--width", "-w", help="Width of window in pixels."),
    height: int = typer.Option(
        1024, "--height", "-h", help="Height of window in pixels."
    ),
    num_rooms: int = typer.Option(
        50, "--rooms", "-r", help="Number of rooms in the dungeon."
    ),
):

    dungeon = DungeonWindow(width, height, num_rooms)

    dungeon.setup()

    arcade.run()
