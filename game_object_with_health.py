from game_object import GameObject
from health import Health
from typing import Dict, Any, Optional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game
from tag import Tag

class GameObjectWithHealth(GameObject):
    """
    Game object with health system.
    Can take damage and die when health is depleted.
    """
    def __init__(self, game:'Game', x: float = 0, y: float = 0, 
                 width: float = 0, height: float = 0, max_health: float = 100, tag: Tag = Tag.EMPTY,
                 z_index: int = 0):
        """
        Initialize a new game object with health.
        
        Args:
            game (Game): Reference to the game instance
            x (float): Initial x position
            y (float): Initial y position
            width (float): Width of the object
            height (float): Height of the object
            max_health (float): Maximum health points
            tag (Tag): Tag for categorizing the object
            z_index (int): Rendering order (higher values are rendered on top)
        """
        super().__init__(game=game, x=x, y=y, width=width, height=height, tag=tag, z_index=z_index)
        self.health = Health(max_health)
    
    def getHit(self, damage: float) -> float:
        """
        Apply damage to the object.
        
        Args:
            damage (float): Amount of damage to apply
            
        Returns:
            float: Remaining health
        """
        remaining_health = self.health.addHealth(-damage)
        if self.health.isDepleted():
            self.die()
        return remaining_health
    
    def heal(self, amount: float) -> float:
        """
        Heal the object.
        
        Args:
            amount (float): Amount of healing to apply
            
        Returns:
            float: New health value
        """
        return self.health.addHealth(amount)
    
    def getCurrentHealth(self) -> float:
        """
        Get current health.
        
        Returns:
            float: Current health
        """
        return self.health.getHealth()
    
    def getMaxHealth(self) -> float:
        """
        Get maximum health.
        
        Returns:
            float: Maximum health
        """
        return self.health.getMaxHealth()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the game object to a dictionary for sending to clients.
        Include health information.
        
        Returns:
            dict: Game object data with health
        """
        data = super().to_dict()
        data['health'] = {
            'current': self.health.getHealth(),
            'max': self.health.getMaxHealth()
        }
        return data
