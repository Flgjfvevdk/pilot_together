from key_touch import KeyTouch
from vector import Vector
from collider import Collider
from typing import List, Dict, Optional, Union, Any

class GameObject:
    """
    Base class for all game objects.
    All game objects have a position and can be updated.
    """
    def __init__(self, x: float = 0, y: float = 0, width: float = 0, height: float = 0):
        """
        Initialize a new game object.
        
        Args:
            x (float): Initial x position
            y (float): Initial y position
            width (float): Width of the object
            height (float): Height of the object
        """
        self.position: Vector = Vector(x, y)
        self.width: float = width
        self.height: float = height
        self.active: bool = True
        self.colliders: List[Collider] = []  # List of colliders
        
        # Image properties
        self.image_url: Optional[str] = None  # Path to image file
        self.image_width: float = 0
        self.image_height: float = 0
        self.image_angle: float = 0  # Rotation in radians
        self.image_opacity: float = 1.0
    
    def get_position(self) -> Vector:
        """
        Get the current position of the object.
        
        Returns:
            Vector: position vector
        """
        return self.position
    
    def set_position(self, x: Union[float, Vector], y: Optional[float] = None) -> None:
        """
        Set the position of the object.
        
        Args:
            x (float or Vector): New x position or Vector position
            y (float, optional): New y position if x is not a Vector
        """
        if isinstance(x, Vector):
            self.position = x.copy()
        else:
            self.position.x = x
            if y is not None:
                self.position.y = y
    
    def add_collider(self, width: float, height: float, offset_x: float = 0, offset_y: float = 0, angle: float = 0) -> int:
        """
        Add a collider to this game object.
        
        Args:
            width (float): Width of the collider
            height (float): Height of the collider
            offset_x (float): X offset from object's position
            offset_y (float): Y offset from object's position
            angle (float): Rotation angle in radians
            
        Returns:
            int: Index of the added collider
        """
        collider: Collider = Collider(width, height, offset_x, offset_y, angle)
        self.colliders.append(collider)
        return len(self.colliders) - 1
    
    def remove_collider(self, index: Optional[int] = None) -> None:
        """
        Remove a collider from this game object.
        
        Args:
            index (int, optional): Index of the collider to remove, removes all if None
        """
        if index is None:
            self.colliders = []
        elif 0 <= index < len(self.colliders):
            self.colliders.pop(index)
    
    def has_collider(self) -> bool:
        """Check if this object has any colliders."""
        return len(self.colliders) > 0
    
    def set_image(self, image_url: str, width: Optional[float] = None, height: Optional[float] = None, angle: float = 0, opacity: float = 1.0) -> None:
        """
        Set an image for this game object.
        
        Args:
            image_url (str): URL or path to the image
            width (float, optional): Display width, defaults to object width
            height (float, optional): Display height, defaults to object height
            angle (float, optional): Rotation angle in radians
            opacity (float, optional): Image opacity (0.0 to 1.0)
        """
        self.image_url = image_url
        self.image_width = width or self.width
        self.image_height = height or self.height
        self.image_angle = angle
        self.image_opacity = max(0.0, min(1.0, opacity))  # Clamp between 0 and 1
    
    def has_image(self) -> bool:
        """Check if this object has an image."""
        return self.image_url is not None
    
    def collides_with(self, other: 'GameObject') -> bool:
        """
        Check if this object collides with another object.
        
        Args:
            other (GameObject): The other game object
            
        Returns:
            bool: True if any colliders intersect, False otherwise
        """
        if not self.active or not other.active:
            return False
            
        if not self.has_collider() or not other.has_collider():
            return False
        
        # Check if any of this object's colliders intersect with any of the other object's colliders
        for my_collider in self.colliders:
            for other_collider in other.colliders:
                if my_collider.intersects(other_collider, self.position, other.position):
                    return True
        
        return False
    
    def update(self, players: Dict, player_keys: Dict[int, Dict[str, KeyTouch]], delta_time: float) -> None:
        """
        Update the object state. Must be overridden by subclasses.
        
        Args:
            players (dict): Dictionary of players
            player_keys (dict[int, dict[str, KeyTouch]]): Dictionary of player keys
            delta_time (float): Time elapsed since last update in seconds
        """
        pass
    
    def get_bounds(self) -> tuple:
        """
        Get the bounding box of the object.
        
        Returns:
            tuple: (x, y, width, height)
        """
        return (self.position.x, self.position.y, self.width, self.height)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the game object to a dictionary for sending to clients.
        
        Returns:
            dict: Game object data
        """
        data: Dict[str, Any] = {
            'x': self.position.x,
            'y': self.position.y,
            'width': self.width,
            'height': self.height,
            'active': self.active
        }
        
        # Add colliders data if present
        if self.has_collider():
            data['colliders'] = [collider.to_dict() for collider in self.colliders]
            
        # Add image data if present
        if self.has_image():
            data['image'] = {
                'url': self.image_url,
                'width': self.image_width,
                'height': self.image_height,
                'angle': self.image_angle,
                'opacity': self.image_opacity
            }
            
        return data

    def die(self) -> None:
        """
        Mark this object as inactive.
        """
        self.active = False
