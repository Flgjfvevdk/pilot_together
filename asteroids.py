from game_objects import GameObject
from vector import Vector
from typing import Dict, Any, Optional


class Asteroid(GameObject):
    """
    Represents an asteroid that moves in a specific direction.
    """
    def __init__(self, x: float, y: float, direction: Vector, speed: float = 40):
        """
        Initialize an asteroid.

        Args:
            x (float): Initial x position as percentage (0-100).
            y (float): Initial y position as percentage (0-100).
            direction (Vector): Direction of movement.
            speed (float): Speed of the asteroid.
        """
        super().__init__(x, y, width=5, height=5)
        self.speed: float = speed
        self.direction: Vector = direction.normalize()  # Ensure the direction is a unit vector
        self.set_image('/static/img/white.png', self.width, self.height)

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
