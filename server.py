from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import socket
import logging
import tkinter as tk
import threading
import time
import math
from game import Game
from game_manager_window import GameManagerWindow

# Set up logging
logging.basicConfig(level=logging.INFO)
# Filter out werkzeug polling logs
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'pilot_together_secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Create the game instance
game = Game(socketio)

# Global variable for game manager window
game_manager = None

@app.route('/')
def index():
    """Serve the main game page"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle new player connection"""
    player_id = request.sid
    player_data = game.add_player(player_id, f'Player {len(game.get_players())}')
    logging.info(f"New player connected: {player_id}")
    
    # Notify everyone about the new player
    emit('player_joined', player_data, broadcast=True)
    
    # Send the current player list to the new player
    emit('player_list', game.get_players())
    
    # Update the game manager window
    if game_manager:
        game_manager.root.after(0, lambda: game_manager.update_player_list(game.get_players()))
        game_manager.root.after(0, lambda: game_manager.update_status(f"New player connected: {player_data['name']}"))

# Modification de la liste des touches
@socketio.on('set_name')
def handle_set_name(data):
    """Handle player name change"""
    player_id = request.sid
    if 'name' in data:
        player_data = game.update_player_name(player_id, data['name'])
        if player_data:
            # Notify everyone about the name change
            emit('player_updated', player_data, broadcast=True)
            
            # Update the game manager window
            if game_manager:
                game_manager.root.after(0, lambda: game_manager.update_player_list(game.get_players()))
                game_manager.root.after(0, lambda: game_manager.update_status(
                    f"Player renamed: {player_data['name']}"
                ))

@socketio.on('disconnect')
def handle_disconnect():
    """Handle player disconnection"""
    player_id = request.sid
    player_data = game.remove_player(player_id)
    if player_data:
        logging.info(f"Player disconnected: {player_id}")
        
        # Notify everyone about the player leaving
        emit('player_left', player_data, broadcast=True)
        
        # Update the game manager window
        if game_manager:
            game_manager.root.after(0, lambda: game_manager.update_player_list(game.get_players()))
            game_manager.root.after(0, lambda: game_manager.update_status(f"Player left: {player_data['name']}"))

@socketio.on('request_game_state')
def handle_request_game_state():
    """Handle player requesting the current game state"""
    emit('game_state_update', game.get_state())

@socketio.on('key_down')
def handle_key_down(data):
    """Handle key press"""
    player_id = request.sid
    if 'key' in data:
        game.handle_key_press(player_id, data['key'], time.time())

@socketio.on('key_up')
def handle_key_up(data):
    """Handle key release"""
    player_id = request.sid
    if 'key' in data:
        game.handle_key_release(player_id, data['key'])

@socketio.on('repair')
def handle_repair():
    """
    Handle repair requests from clients.
    """
    # Heal via la méthode spaceship.repair(), qui émet déjà health_update
    game.spaceship.repair()

@socketio.on('weapon_select')
def handle_weapon_select(data):
    """
    Handle weapon selection change from a player.
    
    Args:
        data: Dictionary with weapon selection
    """
    player_id = request.sid
    if 'weapon' in data:
        weapon = data['weapon']
        if player_id in game.player_keys and 'weapon' in game.player_keys[player_id]:
            game.player_keys[player_id]['weapon'].set_value(weapon)
            logging.info(f"Player {player_id} selected weapon {weapon}")

@socketio.on('rotate_shoot')
def handle_rotate_shoot(data):
    """
    Handle rotating cannon shoot request.
    """
    player_id = request.sid
    if player_id in game.player_keys:
        # Mettre à jour l'angle si présent
        if 'angle' in data:
            angle = data.get('angle', 0)
            game.handle_key_value_update(player_id, 'angle', angle)
        
        # Activer ou désactiver le tir
        if 'firing' in data:
            if data['firing']:
                game.handle_key_press(player_id, 'shoot', time.time())
            else:
                game.handle_key_release(player_id, 'shoot')

def get_local_ip():
    """Get the local IP address to display connection info"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def start_flask(host, port):
    """Start the Flask server in a separate thread"""
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 5000
    print(f"Game server starting!")
    print(f"Players can join at: http://{local_ip}:{port}")
    
    # Create and start the Tkinter window
    root = tk.Tk()
    game_manager = GameManagerWindow(root)
    game_manager.set_game(game)  # Pass the game instance to the window
    game_manager.update_status(f"Server running at http://{local_ip}:{port}")
    
    # Start the game
    game.start()
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=start_flask, args=('0.0.0.0', port))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run the Tkinter main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Shutting down server...")
        game.stop()
        root.quit()
