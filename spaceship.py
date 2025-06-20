from game_object_with_health import GameObjectWithHealth
from key_touch import KeyTouch
from spacecannon import SpaceCannon
from vector import Vector
from typing import Dict, Optional, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game
from tag import Tag

class SpaceShip(GameObjectWithHealth):
    """
    A spaceship that can be controlled by players.
    """
    def __init__(self, game:'Game', x: float = 50, y: float = 50, speed: float = 25, 
                 max_health: float = 100, socketio=None, z_index: int = 10):
        """
        Initialize a new spaceship.
        
        Args:
            game (Game): Reference to the game instance
            x (float): Initial x position as percentage (0-100)
            y (float): Initial y position as percentage (0-100)
            speed (float): Speed of the spaceship in units per second
            max_health (float): Maximum health of the spaceship
            socketio: Socket.IO instance for real-time updates
            z_index (int): Rendering order (higher values are rendered on top)
        """
        super().__init__(game=game, x=x, y=y, width=8, height=8, max_health=max_health, tag=Tag.PLAYER, z_index=z_index)
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
        
        self.set_image('/static/img/spaceship.png', self.width, self.height)

        self.init_space_cannons_direction()

    def init_space_cannons_direction(self, reload_time: float = 1.0) -> None:
        self.space_cannons_directions: Dict[str, SpaceCannon] = {
            'up': SpaceCannon(
                x=self.position.x,
                y=self.position.y,
                direction=Vector(0, -1),
                game=self.game,
                targets=[Tag.ENEMY],
                reload_time=reload_time),
                
            'down': SpaceCannon(
                x=self.position.x,
                y=self.position.y,
                direction=Vector(0, 1),
                game=self.game,
                targets=[Tag.ENEMY],
                reload_time=reload_time),
            'left': SpaceCannon(
                x=self.position.x,
                y=self.position.y,
                direction=Vector(-1, 0),
                game=self.game,
                targets=[Tag.ENEMY],
                reload_time=reload_time),
            'right': SpaceCannon(
                x=self.position.x,
                y=self.position.y,
                direction=Vector(1, 0),
                game=self.game,
                targets=[Tag.ENEMY],
                reload_time=reload_time)
        }
        self.linked_game_objects = list(self.space_cannons_directions.values()).copy()


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
            move_vector: Vector = move_vector_direction.normalize() * speed
            
            new_position: Vector = self.position + move_vector
            
            new_position.x = max(0, min(self.max_x, new_position.x))
            new_position.y = max(0, min(self.max_y, new_position.y))

            self.position = new_position
            
            real_movement = new_position - old_position
            for linked_object in self.linked_game_objects:
                linked_object.position += real_movement
        
        return old_position != self.position
    
    def update(self, players: Dict, player_keys: Dict[int, Dict[str, KeyTouch]], delta_time: float):
        """
        Update the spaceship state based on player inputs.
        
        Args:
            players (dict): Dictionary of players
            player_keys (dict[int, dict[str, KeyTouch]]): Dictionary of player keys
            delta_time (float): Time elapsed since last update in seconds
        """
        self.manage_movement(player_keys, delta_time)
        self.manage_cannon(player_keys)
        
        
    def manage_movement(self, player_keys: Dict[int, Dict[str, KeyTouch]], delta_time:float) -> None:
        move_vector: Vector = Vector(0, 0)
        for keys in player_keys.values():
            for key in keys.values():
                if key.is_active():
                    if key.key_name in ['up', 'down', 'left', 'right']:
                        move_vector += Vector.from_direction(key.key_name)
        if move_vector.magnitude() > 0:
            self.move(move_vector, self.speed * delta_time)


    def manage_cannon(self, player_keys: Dict[int, Dict[str, KeyTouch]]) -> None:
        """
        Handle input for the space cannon based on player keys.
        
        Args:
            player_keys (dict[int, dict[str, KeyTouch]]): Dictionary of player keys
        """
        direction_shoot:Dict[str, bool] = {
            'shoot_up': False,
            'shoot_down': False,
            'shoot_left': False,
            'shoot_right': False
        }
        for keys in player_keys.values():
            for key in keys.values():
                if key.is_active() and key.key_name in direction_shoot:
                    direction_shoot[key.key_name] = True

        for dir, isActive in direction_shoot.items():
            if isActive:
                dir_shot:str = dir.removeprefix("shoot_")
                self.space_cannons_directions[dir_shot].shoot(damage=10.0)


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

