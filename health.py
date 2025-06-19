class Health:
    """
    Class for managing health points for game objects.
    """
    def __init__(self, max_health: float):
        """
        Initialize with maximum health value.
        
        Args:
            max_health (float): Maximum health points
        """
        self.max_health: float = max_health
        self.current_health: float = max_health
    
    def addHealth(self, amount: float) -> float:
        """
        Add (or subtract) health points.
        
        Args:
            amount (float): Amount to add (negative to subtract)
            
        Returns:
            float: New current health value
        """
        self.current_health += amount
        # Clamp health between 0 and max_health
        self.current_health = max(0, min(self.max_health, self.current_health))
        return self.current_health
    
    def getHealth(self) -> float:
        """
        Get current health value.
        
        Returns:
            float: Current health
        """
        return self.current_health
    
    def getMaxHealth(self) -> float:
        """
        Get maximum health value.
        
        Returns:
            float: Maximum health
        """
        return self.max_health
    
    def isDepleted(self) -> bool:
        """
        Check if health is depleted (zero).
        
        Returns:
            bool: True if health is zero
        """
        return self.current_health <= 0
    
    def isFullHealth(self) -> bool:
        """
        Check if health is at maximum.
        
        Returns:
            bool: True if health is at maximum
        """
        return self.current_health >= self.max_health
    
    def setHealth(self, health: float) -> None:
        """
        Set health to a specific value.
        
        Args:
            health (float): New health value
        """
        self.current_health = max(0, min(self.max_health, health))
    
    def setMaxHealth(self, max_health: float) -> None:
        """
        Set maximum health.
        
        Args:
            max_health (float): New maximum health value
        """
        self.max_health = max_health
        # Make sure current health doesn't exceed new max
        self.current_health = min(self.current_health, self.max_health)
