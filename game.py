import time
import logging
import threading
from spaceship import SpaceShip
from key_touch import KeyTouch
from game_objects import GameObject

class Game:
    """
    Main game class that manages the game state, objects, and logic.
    """
    def __init__(self, socketio=None):
        """
        Initialize a new game instance.
        
        Args:
            socketio: The SocketIO instance for emitting updates to clients
        """
        self.socketio = socketio
        self.running:bool = False
        self.update_thread = None
        self.update_interval = 0.05  # 20 updates per second
        
        # Game objects
        self.spaceship:SpaceShip = SpaceShip()
        self.game_objects:dict[str, GameObject] = {}  # Dictionary of game objects by ID
        self.next_object_id = 1  # For generating unique object IDs
        
        # Add spaceship as a game object
        self.add_game_object(self.spaceship, "spaceship")
        
        # Player tracking
        self.players:dict = {}  # player_id -> player data
        self.player_keys:dict[int, dict[str, KeyTouch]] = {}  # player_id -> key states
        
        # Game state
        self.last_active_player = None
        self.last_update_time = None
        
    def start(self):
        """Start the game loop in a separate thread"""
        if self.running:
            return
            
        self.running = True
        self.last_update_time = time.time()
        self.update_thread = threading.Thread(target=self._game_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        logging.info("Game loop started")
        
    def stop(self):
        """Stop the game loop"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1.0)
            logging.info("Game loop stopped")
    
    def _game_loop(self):
        """Main game update loop - runs in a separate thread"""
        while self.running:
            current_time = time.time()
            delta_time = current_time - self.last_update_time
            self.last_update_time = current_time
            
            # Update game state
            self.update(delta_time)
            
            # Sleep to maintain update frequency
            time.sleep(self.update_interval)
    
    def add_game_object(self, obj, obj_id=None):
        """
        Add a game object to the game.
        
        Args:
            obj (GameObject): The game object to add
            obj_id (str, optional): ID for the object, auto-generated if None
            
        Returns:
            str: The object ID
        """
        if obj_id is None:
            obj_id = f"obj_{self.next_object_id}"
            self.next_object_id += 1
            
        self.game_objects[obj_id] = obj
        return obj_id
    
    def remove_game_object(self, obj_id):
        """
        Remove a game object from the game.
        
        Args:
            obj_id (str): ID of the game object to remove
            
        Returns:
            GameObject or None: The removed object if found
        """
        if obj_id in self.game_objects:
            obj = self.game_objects[obj_id]
            del self.game_objects[obj_id]
            return obj
        return None
    
    def get_game_object(self, obj_id):
        """
        Get a game object by ID.
        
        Args:
            obj_id (str): ID of the game object
            
        Returns:
            GameObject or None: The game object if found
        """
        return self.game_objects.get(obj_id)
    
    def update(self, delta_time):
        """
        Update all game objects and process player input.
        
        Args:
            delta_time (float): Time elapsed since last update
        """
        # Process player inputs and update spaceship
        ship_moved = self.spaceship.update(self.players, self.player_keys, delta_time)

        # Update all other game objects
        for obj_id, obj in list(self.game_objects.items()):  # Use list to avoid modification during iteration
            if obj != self.spaceship:  # Skip spaceship as it's already updated
                obj.update(self.players, self.player_keys, delta_time)
        
        # Check collisions between game objects
        self.check_collisions()
        
        # Emit game state to clients if anything changed
        if ship_moved and self.socketio:
            game_state = self.get_state()
            self.socketio.emit('game_state_update', game_state)
    
    def check_collisions(self):
        """Check for collisions between game objects."""
        # Get list of objects with colliders
        collider_objects = [(obj_id, obj) for obj_id, obj in self.game_objects.items() 
                           if obj.has_collider() and obj.active]
        
        # Check each pair of objects
        for i in range(len(collider_objects)):
            for j in range(i + 1, len(collider_objects)):
                obj1_id, obj1 = collider_objects[i]
                obj2_id, obj2 = collider_objects[j]
                
                if obj1.collides_with(obj2):
                    # Objects are colliding - handle the collision
                    self.handle_collision(obj1_id, obj1, obj2_id, obj2)
    
    def handle_collision(self, obj1_id, obj1, obj2_id, obj2):
        """
        Handle a collision between two game objects.
        
        Args:
            obj1_id (str): ID of the first object
            obj1 (GameObject): First game object
            obj2_id (str): ID of the second object
            obj2 (GameObject): Second game object
        """
        # For now, just log the collision
        # This could be expanded to handle specific collision interactions
        logging.debug(f"Collision detected between {obj1_id} and {obj2_id}")
    
    def get_state(self):
        """
        Get the current game state for sending to clients.
        
        Returns:
            dict: Current game state
        """
        # Include the spaceship state
        state = self.spaceship.to_dict()
        
        # Add all game objects (except spaceship which is handled separately)
        game_objects = []
        for obj_id, obj in self.game_objects.items():
            if obj != self.spaceship:  # Skip spaceship as it's already included
                obj_data = obj.to_dict()
                obj_data['id'] = obj_id
                game_objects.append(obj_data)
        
        state['gameObjects'] = game_objects
        return state
    
    def add_player(self, player_id, name):
        """
        Add a new player to the game.
        
        Args:
            player_id (str): Unique player identifier
            name (str): Player's display name
        """
        self.players[player_id] = {
            'id': player_id,
            'name': name
        }
        
        # Initialize player's key states
        self.player_keys[player_id] = {
            'up': KeyTouch('up'),
            'down': KeyTouch('down'),
            'left': KeyTouch('left'),
            'right': KeyTouch('right')
        }
        
        logging.info(f"Player {name} (ID: {player_id}) joined the game")
        return self.players[player_id]
    
    def remove_player(self, player_id):
        """
        Remove a player from the game.
        
        Args:
            player_id (str): Player's unique identifier
            
        Returns:
            dict or None: Removed player's data or None if player wasn't found
        """
        if player_id in self.players:
            player_data = self.players[player_id]
            del self.players[player_id]
            
            # Clean up player's key states
            if player_id in self.player_keys:
                del self.player_keys[player_id]
                
            logging.info(f"Player {player_data['name']} (ID: {player_id}) left the game")
            return player_data
        return None
    
    def update_player_name(self, player_id, name):
        """
        Update a player's name.
        
        Args:
            player_id (str): Player's unique identifier
            name (str): New player name
            
        Returns:
            dict or None: Updated player data or None if player wasn't found
        """
        if player_id in self.players:
            self.players[player_id]['name'] = name
            return self.players[player_id]
        return None
    
    def get_players(self):
        """
        Get list of all players.
        
        Returns:
            list: All player data
        """
        return list(self.players.values())
    
    def handle_key_press(self, player_id, key_name, timestamp=None):
        """
        Handle a key press event from a player.
        
        Args:
            player_id (str): Player's unique identifier
            key_name (str): Key that was pressed
            timestamp (float, optional): When the key was pressed
        """
        if player_id in self.player_keys and key_name in self.player_keys[player_id]:
            self.player_keys[player_id][key_name].press(timestamp)
            logging.debug(f"Player {player_id} pressed {key_name}")
    
    def handle_key_release(self, player_id, key_name):
        """
        Handle a key release event from a player.
        
        Args:
            player_id (str): Player's unique identifier
            key_name (str): Key that was released
        """
        if player_id in self.player_keys and key_name in self.player_keys[player_id]:
            self.player_keys[player_id][key_name].release()
            logging.debug(f"Player {player_id} released {key_name}")
    
    def get_last_active_player(self):
        """
        Get the name of the last player who moved the ship.
        
        Returns:
            str or None: Player name or None if no player has moved the ship
        """
        return self.last_active_player
