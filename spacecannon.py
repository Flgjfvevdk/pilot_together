from game_object import GameObject
from vector import Vector
from projectile import Projectile
from tag import Tag
from typing import List, Optional, Any, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from game import Game

class SpaceCannon:
    """
    A space cannon that can shoot projectiles in a specified direction.
    """
    def __init__(self, x: float, y: float, direction:Vector, 
                 game: 'Game', projectile_speed: float = 1.0, 
                 targets: List[Tag] = None,
                 img_url:str='/static/img/green.png', 
                 projectile_width: float = 3, projectile_height: float = 3, reload_time: float = 1):
        """
        Initialize a new space cannon.
        
        Args:
            x (float): X position of the cannon
            y (float): Y position of the cannon
            game_reference: Reference to the game instance for adding projectiles
            projectile_speed (float): Speed of the projectiles fired
            targets (List[Tag]): List of tags that projectiles can damage
            projectile_width (float): Width of the projectiles
            projectile_height (float): Height of the projectiles
        """
        self.position = Vector(x, y)
        self.direction:Vector = direction.copy()
        self.game:Game = game
        self.projectile_speed = projectile_speed
        self.targets = targets or [Tag.ENEMY]  # Default to targeting enemies
        self.img_projectile_path:str = img_url
        self.projectile_width = projectile_width
        self.projectile_height = projectile_height
        self.reload_time: float = reload_time
        self.last_shot_time: float = 0  # Track when the cannon was last fired
        
    def shoot(self, damage: float, direction: Vector = None) -> Optional[str]:
        """
        Shoot a projectile in the specified direction.
        
        Args:
            direction (Vector): Direction to shoot the projectile
            damage (float): Amount of damage the projectile will deal
            
        Returns:
            Optional[str]: ID of the created projectile, or None if failed
        """
        if self.game is None:
            return None
        
        # Check if enough time has elapsed since the last shot
        current_time = time.time()
        if current_time - self.last_shot_time < self.reload_time:
            return None  # Not ready to fire yet
        
        if direction is None:
            direction = self.direction

        # Create a projectile at the cannon's position
        projectile = Projectile(
            game=self.game,
            x=self.position.x,
            y=self.position.y,
            direction=direction,
            speed=self.projectile_speed,
            damage=damage,
            targets=self.targets,
            img_url=self.img_projectile_path,
            width=self.projectile_width,
            height=self.projectile_height
        )
        
        # Add the projectile to the game
        projectile_id = self.game.add_game_object(projectile)
        
        # Update the last shot time
        self.last_shot_time = current_time
        
        return projectile_id
    
    def set_position(self, x: float, y: float) -> None:
        """
        Update the position of the space cannon.
        
        Args:
            x (float): New X position
            y (float): New Y position
        """
        self.position.x = x
        self.position.y = y
