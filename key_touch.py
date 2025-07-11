from typing import Dict, Optional, Any

class KeyTouch:
    """
    Represents a keyboard key that can be pressed or released.
    Used to track player input state.
    """
    def __init__(self, key_name: str, value: Any = None):
        """
        Initialize a new key touch.
        
        Args:
            key_name (str): The name/identifier of the key
            value (any): Optional value associated with this key
        """
        self.key_name: str = key_name
        self.is_pressed: bool = False
        self.last_pressed: float = 0  # Timestamp of last press
        self.value = value  # Added value for storing weapon selection
    
    def press(self, timestamp: Optional[float] = None) -> bool:
        """
        Mark the key as pressed.
        
        Args:
            timestamp (float, optional): The time when the key was pressed
        
        Returns:
            bool: True if the state changed, False otherwise
        """
        if not self.is_pressed:
            self.is_pressed = True
            self.last_pressed = timestamp if timestamp is not None else 0
            return True
        return False
    
    def release(self) -> bool:
        """
        Mark the key as released.
        
        Returns:
            bool: True if the state changed, False otherwise
        """
        if self.is_pressed:
            self.is_pressed = False
            return True
        return False
    
    def is_active(self) -> bool:
        """
        Check if the key is currently pressed.
        
        Returns:
            bool: True if the key is pressed, False otherwise
        """
        return self.is_pressed
    
    def set_value(self, value: Any) -> None:
        """
        Set the value associated with this key.
        
        Args:
            value (any): The new value
        """
        self.value = value
        
    def get_value(self) -> Any:
        """
        Get the value associated with this key.
        
        Returns:
            any: The value
        """
        return self.value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the key state to a dictionary.
        
        Returns:
            dict: The key state
        """
        return {
            'key': self.key_name,
            'pressed': self.is_pressed
        }
