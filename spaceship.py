from game_object_with_health import GameObjectWithHealth
from key_touch import KeyTouch
from spacecannon import SpaceCannon
from shield_cannon import ShieldCannon
from vector import Vector
from typing import Dict, Optional, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game
from tag import Tag
from overheat import Overheat
import math

class SpaceShip(GameObjectWithHealth):
    """
    A spaceship that can be controlled by players.
    """
    def __init__(self, game:'Game', x: float = 50, y: float = 50, speed: float = 25, 
                 max_health: float = 100, socketio=None, z_index: int = 10, 
                 projectile_speed: float = 200.0, projetile_damage: float = 5.0, reload_time: float = 0.3):
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
        super().__init__(game=game, x=x, y=y, width=6, height=6, max_health=max_health, tag=Tag.PLAYER, z_index=z_index)
        self.speed: float = speed  # Units per second
        self.max_x: float = 100  # Maximum x coordinate (percentage)
        self.max_y: float = 100  # Maximum y coordinate (percentage)
        self.socketio = socketio  # Socket.IO pour les mises à jour en temps réel

        self.repair_value: float = 1.0 
        
        # Set up collider (slightly smaller than the ship for better gameplay)
        self.add_collider(
            width=self.width * 0.8, 
            height=self.height * 0.8,
            offset_x=0,
            offset_y=0
        )

        self.projectile_speed: float = projectile_speed  
        self.reload_time: float = reload_time 
        self.projetile_damage: float = projetile_damage
        
        self.set_image('/static/img/spaceship.png', self.width, self.height)

        self.init_space_cannons_direction(reload_time=self.reload_time, speed=self.projectile_speed)
        
        # Overheat management
        self.overheat = Overheat()
        self.init_shield_cannon()  # Nouvelle méthode simplifiée
        self.heat_shoot = 3.0
        self.heat_shield = 20.0  # Augmenté car il n'y a qu'un seul shield plus puissant

        # Initialisation des 4 canons rotatifs (tous identiques)
        self.rotating_cannons = {}
        for i in range(1, 5):  # Canons 1 à 4
            self.rotating_cannons[i] = SpaceCannon(
                x=self.position.x, y=self.position.y,
                direction=Vector(1, 0),
                game=self.game,
                reload_time=self.reload_time,
                projectile_speed=self.projectile_speed,
                img_url='/static/img/green.png',
                projectile_width=3, projectile_height=3
            )
        
        # Ajouter tous les canons aux objets liés
        for cannon in self.rotating_cannons.values():
            self.linked_game_objects.append(cannon)

    def init_space_cannons_direction(self, reload_time: float = 0.4, speed:float = 150.0) -> None:
        self.space_cannons_directions: Dict[str, SpaceCannon] = {
            'up': SpaceCannon(
                x=self.position.x,
                y=self.position.y,
                direction=Vector(0, -1),
                game=self.game,
                targets=[Tag.ENEMY],
                reload_time=reload_time,
                projectile_speed=speed),
                
            'down': SpaceCannon(
                x=self.position.x,
                y=self.position.y,
                direction=Vector(0, 1),
                game=self.game,
                targets=[Tag.ENEMY],
                reload_time=reload_time,
                projectile_speed=speed),
            'left': SpaceCannon(
                x=self.position.x,
                y=self.position.y,
                direction=Vector(-1, 0),
                game=self.game,
                targets=[Tag.ENEMY],
                reload_time=reload_time,
                projectile_speed=speed),
            'right': SpaceCannon(
                x=self.position.x,
                y=self.position.y,
                direction=Vector(1, 0),
                game=self.game,
                targets=[Tag.ENEMY],
                reload_time=reload_time,
                projectile_speed=speed)
        }
        self.linked_game_objects = list(self.space_cannons_directions.values()).copy()

    def init_shield_cannon(self) -> None:
        """Initialise un seul canon de bouclier stationnaire."""
        self.shield_cannon = ShieldCannon(
            x=self.position.x,
            y=self.position.y,
            direction=Vector(0, 0),  # Direction non utilisée car vitesse = 0
            game=self.game,
            speed=0.0,  # Le bouclier reste sur place
            reload_time=5.0, 
            barrier_lifespan=3.0,  
            width=24.0, 
            height=24.0 
        )

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
        if self.overheat.can_act():
            self.manage_cannon(player_keys)
            self.manage_shield(player_keys)
            self.manage_rotate_cannon(player_keys)  # Nouveau: gère le canon rotatif
        
        # Overheat cooling key
        cool_active = any(
            keys.get('cool') and keys['cool'].is_active()
            for keys in player_keys.values()
        )
        if cool_active:
            self.overheat.cool_down(delta_time)
        else:
            self.overheat.stop_cooling()

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
            if isActive :
                dir_shot = dir.removeprefix("shoot_")
                has_shoot:bool = self.space_cannons_directions[dir_shot].shoot(damage=self.projetile_damage)
                if has_shoot:
                    self.overheat.add_heat(self.heat_shoot)

    def manage_shield(self, player_keys: Dict[int, Dict[str, KeyTouch]]) -> None:
        """
        Gère l'activation du bouclier basé sur les touches des joueurs.
        
        Args:
            player_keys (dict[int, dict[str, KeyTouch]]): Dictionnaire des touches des joueurs
        """
        # Mise à jour de la position du canon
        self.shield_cannon.set_position(self.position.x, self.position.y)
        
        # Vérification si la touche shield est pressée par un joueur
        shield_active = any(
            keys.get('shield') and keys['shield'].is_active()
            for keys in player_keys.values()
        )
        
        if shield_active:
            has_shoot = self.shield_cannon.shoot()
            if has_shoot:
                self.overheat.add_heat(self.heat_shield)

    def manage_rotate_cannon(self, player_keys: Dict[int, Dict[str, KeyTouch]]) -> None:
        """
        Gère le tir du canon rotatif basé sur les touches des joueurs.
        
        Args:
            player_keys (dict[int, dict[str, KeyTouch]]): Dictionnaire des touches des joueurs
        """
        # Recherche un joueur qui tire avec le canon rotatif
        for player_id, keys in player_keys.items():
            if (keys.get('shoot') and keys.get('shoot').is_active() and 
                keys.get('angle') is not None):
                
                # Récupérer l'angle et l'arme sélectionnée
                angle = keys.get('angle').get_value()
                weapon_key = keys.get('weapon')
                weapon = weapon_key.get_value() if weapon_key else 1
                
                # S'assurer que l'arme est dans les limites valides
                weapon = max(1, min(4, weapon))
                
                # Récupérer le canon correspondant à l'arme
                cannon = self.rotating_cannons[weapon]
                
                # Mettre à jour la direction du canon
                dir_vec = Vector.from_angle(math.radians(angle))
                cannon.direction = dir_vec.normalize()
                
                # Mettre à jour la position
                cannon.set_position(self.position.x, self.position.y)
                
                # Tirer avec le canon sélectionné (même dégâts pour tous les canons)
                has_shot = cannon.shoot(damage=self.projetile_damage)
                if has_shot:
                    # Même chaleur générée pour tous les canons
                    self.overheat.add_heat(self.heat_shoot)
                
                

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

    def repair(self) -> float:
        """
        Heal the spaceship and emit a health update event.
        """
        new_health = self.heal(self.repair_value)
        if self.socketio:
            health_data = {
                'health': {
                    'current': new_health,
                    'max': self.getMaxHealth()
                }
            }
            self.socketio.emit('spaceship_health_update', health_data)
        return new_health

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the spaceship data to a dictionary for sending to clients.
        
        Returns:
            dict: Spaceship data
        """
        data = super().to_dict()
        data['temperature'] = self.overheat.temperature
        data['maxTemperature'] = self.overheat.max_temp
        return data

