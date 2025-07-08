import random
from vector import Vector
from asteroids import Asteroid
from enemy_ship import EnemyShip
from game_object import GameObject
from typing import Dict, Optional, Any
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

class Adversity(GameObject):
    """
    Adversity system that spawns asteroids and enemy ships at regular intervals.
    Implemented as a GameObject so it can be updated naturally by the game loop.
    """
    def __init__(self, game_reference:'Game'):
        """
        Initialize the adversity system.

        Args:
            game_reference: Reference to the game instance for adding new objects
        """
        super().__init__(0, 0)  # Position doesn't matter as this is an invisible manager
        self.game:Game = game_reference
        # asteroid spawn
        self.spawn_interval_asteroid: float = 0.5  # Spawn an asteroid every 0.5 seconds by default
        self.last_spawn_time_asteroid: float = 0
        # enemy ship spawn
        self.spawn_interval_enemy: float = 10.0  # Spawn an enemy ship every 10 seconds by default
        self.last_spawn_time_enemy: float = 0.0
        self.active: bool = True
        
        # Damages
        self.asteroid_damage: float = 2.0  # Default asteroid damage
        self.enemy_damage: float = 5.0    # Default enemy projectile damage

    def update(self, players: Dict, player_keys: Dict, delta_time: float) -> None:
        """
        Update method called by the game loop. Spawns asteroids and enemy ships at intervals.

        Args:
            players (dict): Dictionary of players
            player_keys (dict): Dictionary of player keys
            delta_time (float): Time elapsed since last update in seconds
        """
        import time
        current_time: float = time.time()
        
        # Skip spawning if spawn_interval is 0 (disabled)
        if self.spawn_interval_asteroid > 0 and current_time - self.last_spawn_time_asteroid >= self.spawn_interval_asteroid:
            self.spawn_asteroid()
            self.last_spawn_time_asteroid = current_time

        # Check enemy ship spawn
        if self.spawn_interval_enemy > 0 and current_time - self.last_spawn_time_enemy >= self.spawn_interval_enemy:
            self.spawn_enemyship()
            self.last_spawn_time_enemy = current_time

    def spawn_asteroid(self) -> None:
        """
        Spawn a new asteroid at a random position around the edges of the screen.
        """
        # Randomly choose a side (top, bottom, left, right)
        side: str = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x: float = random.uniform(0, 100)
            y: float = -5  # Just above the screen
            direction: Vector = Vector(random.uniform(-1, 1), 1)  # Moving downward
        elif side == 'bottom':
            x: float = random.uniform(0, 100)
            y: float = 105  # Just below the screen
            direction: Vector = Vector(random.uniform(-1, 1), -1)  # Moving upward
        elif side == 'left':
            x: float = -5  # Just left of the screen
            y: float = random.uniform(0, 100)
            direction: Vector = Vector(1, random.uniform(-1, 1))  # Moving right
        else:  # right
            x: float = 105  # Just right of the screen
            y: float = random.uniform(0, 100)
            direction: Vector = Vector(-1, random.uniform(-1, 1))  # Moving left

        # Create the asteroid and add it to the game with configured damage
        asteroid: Asteroid = Asteroid(game=self.game, x=x, y=y, direction=direction, damage=self.asteroid_damage)
        self.game.add_game_object(asteroid)

    def spawn_enemyship(self) -> None:
        """
        Spawn an EnemyShip at a random screen edge with a random inward direction.
        """
        # Choose a side
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.uniform(0, 100);   y = -5
            direction = Vector(random.uniform(-1, 1), 1)
        elif side == 'bottom':
            x = random.uniform(0, 100);   y = 105
            direction = Vector(random.uniform(-1, 1), -1)
        elif side == 'left':
            x = -5;   y = random.uniform(0, 100)
            direction = Vector(1, random.uniform(-1, 1))
        else:  # right
            x = 105;  y = random.uniform(0, 100)
            direction = Vector(-1, random.uniform(-1, 1))

        # Create enemy ship with configured damage
        enemy = EnemyShip(
            game=self.game,
            x=x, y=y,
            direction=direction,
            damage=self.enemy_damage
        )
        self.game.add_game_object(enemy)
