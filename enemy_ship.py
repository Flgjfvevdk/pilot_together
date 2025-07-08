from game_object_with_health import GameObjectWithHealth
from vector import Vector
from projectile import Projectile
from tag import Tag
import time
from typing import Dict, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

class EnemyShip(GameObjectWithHealth):
    """
    Ennemi se déplaçant en ligne droite, rebondissant sur les bords et tirant vers le joueur.
    """
    def __init__(self, game:'Game', x: float, y: float,
                 direction: Vector = Vector(1, 0),
                 speed: float = 25.0, fire_rate: float = 3.0,
                 projectile_speed: float = 50.0, damage: float = 5.0,
                 max_health: float = 15.0, width: float = 4.0, height: float = 4.0):
        super().__init__(game=game, x=x, y=y,
                         width=width, height=height,
                         max_health=max_health, tag=Tag.ENEMY)
        self.direction: Vector = direction.normalize()
        self.speed: float = speed
        self.fire_rate: float = fire_rate
        self.projectile_speed: float = projectile_speed
        self.damage: float = damage
        self.last_shot_time: float = 0.0
        # bornes en pourcentage
        self.min_x, self.max_x = 0.0, 100.0
        self.min_y, self.max_y = 0.0, 100.0
        # visuel & collision
        self.set_image('/static/img/red.png', width, height)
        self.add_collider(width=width*1, height=height*1)

    def update(self, players: Dict[str, Any], player_keys: Dict[str, Any], delta_time: float) -> None:
        # déplacement
        self.position += self.direction * self.speed * delta_time

        # rebonds
        if self.position.x < self.min_x or self.position.x > self.max_x:
            self.direction.x = -self.direction.x
            self.position.x = max(self.min_x, min(self.position.x, self.max_x))
        if self.position.y < self.min_y or self.position.y > self.max_y:
            self.direction.y = -self.direction.y
            self.position.y = max(self.min_y, min(self.position.y, self.max_y))

        
        now = time.time()
        if now - self.last_shot_time >= self.fire_rate:
            direction_player = (self.game.get_spaceship_position() - self.position).normalize()
            proj = Projectile(
                game=self.game,
                x=self.position.x, y=self.position.y,
                direction=direction_player,
                speed=self.projectile_speed,
                damage=self.damage,
                targets=[Tag.PLAYER],
                img_url='/static/img/jaune.png',
                width=2, height=2
            )
            self.game.add_game_object(proj)
            self.last_shot_time = now
