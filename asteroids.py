from game_object_with_health import GameObjectWithHealth
from vector import Vector
from typing import Dict, Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game
from spaceship import SpaceShip
from tag import Tag

class Asteroid(GameObjectWithHealth):
    """
    Represents an asteroid that moves in a specific direction.
    """
    def __init__(self, game:'Game', x: float, y: float, direction: Vector, speed: float = 40, tag= Tag.ENEMY, max_health: float = 10, damage:float = 2.0):
        """
        Initialize an asteroid.

        Args:
            x (float): Initial x position as percentage (0-100).
            y (float): Initial y position as percentage (0-100).
            direction (Vector): Direction of movement.
            speed (float): Speed of the asteroid.
            max_health (float): Maximum health of the asteroid.
        """
        super().__init__(game=game, x=x, y=y, width=5, height=5, max_health=max_health, tag=Tag.ENEMY)
        self.speed: float = speed
        self.damage: float = damage 
        self.direction: Vector = direction.normalize()  # Ensure the direction is a unit vector
        self.set_image('/static/img/jaune.png', self.width, self.height)
        
        # Ajouter un collider carré par défaut
        self.add_collider(
            width=self.width,
            height=self.height,
            offset_x=0,
            offset_y=0
        )

    def update(self, players: Dict[str, Any], player_keys: Dict[str, Any], delta_time: float) -> None:
        """
        Update the asteroid's position.

        Args:
            players (dict): Dictionary of players.
            player_keys (dict): Dictionary of player keys.
            delta_time (float): Time elapsed since the last update.
        """
        move_vector: Vector = self.direction * self.speed * delta_time
        self.position += move_vector

        # Check if the asteroid is out of bounds
        if self.position.x < -10 or self.position.x > 110 or self.position.y < -10 or self.position.y > 110:
            self.active = False  # Mark the asteroid as inactive

    def on_collision(self, other: 'GameObject', other_id: str = None) -> None:
        """
        Handle collision with another game object.
        When an asteroid hits the spaceship, it deals damage and then disappears.
        
        Args:
            other (GameObject): The other game object
            other_id (str, optional): ID of the other game object
        """
        # Check if the other object is the spaceship
        if isinstance(other, SpaceShip):
            remaining_health = other.getHit(self.damage)
            
            # The asteroid is destroyed upon impact
            self.die()
            
            # Log the collision
            import logging
            logging.info(f"Collision: Asteroid hit the spaceship! Remaining health: {remaining_health}")
