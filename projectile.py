from game_object import GameObject
from game_object_with_health import GameObjectWithHealth
from vector import Vector
from tag import Tag
from typing import List, Set, Dict, Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

class Projectile(GameObject):
    """
    A projectile that moves in a straight line and can damage game objects.
    """
    def __init__(self, game:'Game', x: float, y: float, direction: Vector, speed: float = 150,
                 damage: float = 10.0, targets: List[Tag] = None, disappear_on_hit: bool = True,
                 img_url:str='/static/img/green.png', width: float = 2, height: float = 2):
        """
        Initialize a new projectile.
        
        Args:
            game (Game): Reference to the game instance
            x (float): Initial x position
            y (float): Initial y position
            direction (Vector): Direction of movement
            speed (float): Speed of the projectile
            damage (float): Amount of damage to apply on hit
            targets (List[Tag]): List of tags that this projectile can damage
            disappear_on_hit (bool): Whether the projectile should disappear after hitting a target
            width (float): Width of the projectile
            height (float): Height of the projectile
        """
        super().__init__(game=game, x=x, y=y, width=width, height=height)
        self.direction: Vector = direction.normalize()  # Normalize to ensure unit vector
        self.speed: float = speed
        self.damage: float = damage
        self.targets: List[Tag] = targets or [Tag.ENEMY]  # Default to targeting enemies
        self.disappear_on_hit: bool = disappear_on_hit
        self.damaged_objects: Set[str] = set()  # Track objects already damaged

        self.set_image(img_url, self.width, self.height)
        
        # Add a collider
        self.add_collider(width, height)
        
    def update(self, players: Dict, player_keys: Dict, delta_time: float) -> None:
        """
        Update the projectile's position based on its direction and speed.
        
        Args:
            players (dict): Dictionary of players
            player_keys (dict): Dictionary of player keys
            delta_time (float): Time elapsed since last update in seconds
        """
        # Calculate movement vector
        move_vector: Vector = self.direction * self.speed * delta_time
        
        # Update position
        self.position += move_vector
        
        # Check if the projectile is out of bounds (e.g., off-screen)
        if self.position.x < -10 or self.position.x > 110 or self.position.y < -10 or self.position.y > 110:
            self.die()  
    
    def on_collision(self, other: 'GameObject', other_id: str = None) -> None:
        """
        Handle collision with another game object.
        
        Args:
            other (GameObject): The other game object
            other_id (str, optional): ID of the other game object
        """
        # Skip if this object has already been damaged by this projectile
        if other_id in self.damaged_objects:
            return
        
        # Check if the other object has a tag that's in our target list
        if other.tag in self.targets:
            if isinstance(other, GameObjectWithHealth) :
                other.getHit(self.damage)
                self.damaged_objects.add(other_id)
                
                if self.disappear_on_hit:
                    self.die()


