import time
from shield_barrier import ShieldBarrier
from vector import Vector
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from game import Game

class ShieldCannon:
    """
    Cannon for launching ShieldBarrier projectiles in a given direction.
    """
    def __init__(self, x: float, y: float, direction: Vector,
                 game:'Game', speed: float = 10.0, reload_time: float = 1.0,
                 barrier_lifespan: float = 2.0, width: float = 12.0, height: float = 12.0):
        self.position = Vector(x, y)
        self.direction = direction.normalize()
        self.game = game
        self.speed = speed
        self.reload_time = reload_time
        self.last_shot = 0.0
        self.barrier_kwargs = {
            "speed": speed,
            "width": width,
            "height": height,
            "lifespan": barrier_lifespan
        }

    def shoot(self) -> bool:
        now = time.time()
        if now - self.last_shot < self.reload_time:
            return False
        # mettre à jour position
        x, y = self.position.x, self.position.y
        barrier = ShieldBarrier(
            game=self.game,
            x=x, y=y,
            direction=self.direction,
            **self.barrier_kwargs
        )
        self.game.add_game_object(barrier)
        self.last_shot = now
        return True

    def set_position(self, x: float, y: float) -> None:
        self.position.x = x
        self.position.y = y
