from typing import TYPE_CHECKING
from projectile import Projectile
from vector import Vector
from tag import Tag

if TYPE_CHECKING:
    from game import Game

class ShieldBarrier(Projectile):
    """
    Barrier projectile that moves forward and destroys incoming enemy projectiles on collision.
    """
    def __init__(self, game:'Game', x: float, y: float, direction: Vector,
                 speed: float = 20.0, width: float = 12.0, height: float = 12.0,
                 lifespan: float = 2):
        # damage=0, no targets (barrier itself doesn't damage), doesn't disappear on hit
        super().__init__(
            game=game,
            x=x, y=y,
            direction=direction,
            speed=speed,
            damage=0.0,
            targets=[],
            disappear_on_hit=False,
            img_url='/static/img/shield.png',
            width=width,
            height=height
        )
        self.lifespan = lifespan
        self.age = 0.0

    def update(self, players, player_keys, delta_time: float) -> None:
        # Move like a normal projectile
        super().update(players, player_keys, delta_time)
        # Expire after lifespan
        self.age += delta_time
        if self.age >= self.lifespan:
            self.die()

    def on_collision(self, other, other_id: str = None) -> None:
        # Intercept only projectiles targeting the player
        if isinstance(other, Projectile) and Tag.PLAYER in getattr(other, 'targets', []):
            other.die()
