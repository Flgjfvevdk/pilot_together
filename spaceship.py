from game_object_with_health import GameObjectWithHealth
from key_touch import KeyTouch
from vector import Vector
from typing import Dict, Optional, Any

class SpaceShip(GameObjectWithHealth):
    """
    A spaceship that can be controlled by players.
    """
    def __init__(self, x: float = 50, y: float = 50, speed: float = 25, max_health: float = 100, socketio=None):
        """
        Initialize a new spaceship.
        
        Args:
            x (float): Initial x position as percentage (0-100)
            y (float): Initial y position as percentage (0-100)
            speed (float): Speed of the spaceship in units per second
            max_health (float): Maximum health of the spaceship
            socketio: Socket.IO instance for real-time updates
        """
        super().__init__(x, y, width=8, height=8, max_health=max_health)
        self.speed: float = speed  # Units per second
        self.max_x: float = 100  # Maximum x coordinate (percentage)
        self.max_y: float = 100  # Maximum y coordinate (percentage)
        self.socketio = socketio  # Socket.IO pour les mises à jour en temps réel
        
        # Set up collider (slightly smaller than the ship for better gameplay)
        self.add_collider(
            width=self.width * 0.8, 
            height=self.height * 0.8,
            offset_x=0,
            offset_y=0
        )
        
        # Set ship image with relative dimensions
        self.set_image('/static/img/spaceship.png', self.width, self.height)
        
    def move(self, move_vector_direction: Vector, speed: Optional[float] = None) -> bool:
        """
        Move the spaceship in the given direction.
        
        Args:
            move_vector_direction (Vector): Direction to move
            speed (float, optional): Movement speed to use
        
        Returns:
            bool: True if the ship moved, False otherwise
        """
        old_position: Vector = self.position.copy()
        if speed is None:
            speed = self.speed

        if move_vector_direction.magnitude() > 0:
            # Calculate movement vector
            move_vector: Vector = move_vector_direction.normalize() * speed
            
            # Calculate new position
            new_position: Vector = self.position + move_vector
            
            # Apply bounds
            new_position.x = max(0, min(self.max_x, new_position.x))
            new_position.y = max(0, min(self.max_y, new_position.y))
            
            # Update position
            self.position = new_position
        
        # Return True if the position changed
        return old_position != self.position
    
    def update(self, players: Dict, player_keys: Dict[int, Dict[str, KeyTouch]], delta_time: float) -> bool:
        """
        Update the spaceship state based on player inputs.
        
        Args:
            players (dict): Dictionary of players
            player_keys (dict[int, dict[str, KeyTouch]]): Dictionary of player keys
            delta_time (float): Time elapsed since last update in seconds
        """
        ship_moved: bool = False
        move_vector: Vector = Vector(0, 0)
        for keys in player_keys.values():
            for key in keys.values():
                if key.is_active():
                    move_vector += Vector.from_direction(key.key_name)
        if move_vector.magnitude() > 0:
            ship_moved = ship_moved or self.move(move_vector, self.speed * delta_time)
        return ship_moved

    def getHit(self, damage: float) -> float:
        """
        Apply damage to the spaceship and emit a health update event.
        
        Args:
            damage (float): Amount of damage to apply
            
        Returns:
            float: Remaining health
        """
        remaining_health = super().getHit(damage)
        
        # Émettre un événement de mise à jour de santé si socketio est disponible
        if self.socketio:
            health_data = {
                'health': {
                    'current': self.getCurrentHealth(),
                    'max': self.getMaxHealth()
                }
            }
            self.socketio.emit('spaceship_health_update', health_data)
        
        return remaining_health

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the spaceship data to a dictionary for sending to clients.
        
        Returns:
            dict: Spaceship data
        """
        # Utiliser directement la méthode de la classe parente pour assurer la cohérence
        return super().to_dict()
