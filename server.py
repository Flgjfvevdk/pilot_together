from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import socket
import logging
import tkinter as tk
from tkinter import ttk
import threading
import time
from game import Game

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'pilot_together_secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Create the game instance
game = Game(socketio)

# Game Manager Window class
class GameManagerWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Pilot Together - Game Manager")
        self.root.geometry("500x400")
        self.root.configure(bg="#1a1a2e")
        
        # Create header
        header_frame = tk.Frame(root, bg="#1a1a2e")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(header_frame, text="Game Manager", font=("Arial", 16, "bold"), 
                              bg="#1a1a2e", fg="#7ab5ff")
        title_label.pack()
        
        # Create player list frame
        player_frame = tk.Frame(root, bg="#252544")
        player_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        player_header = tk.Label(player_frame, text="Connected Players", font=("Arial", 12), 
                              bg="#252544", fg="#eee")
        player_header.pack(pady=5)
        
        # Create Treeview for player list
        self.player_tree = ttk.Treeview(player_frame, columns=("ID", "Name"), show="headings")
        self.player_tree.heading("ID", text="ID")
        self.player_tree.heading("Name", text="Player Name")
        self.player_tree.column("ID", width=150)
        self.player_tree.column("Name", width=250)
        self.player_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create status bar
        status_frame = tk.Frame(root, bg="#1a1a2e")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Server starting...", 
                                   bg="#1a1a2e", fg="#eee")
        self.status_label.pack(side=tk.LEFT)
        
        # Configure style for Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                      background="#252544", 
                      foreground="#eee", 
                      fieldbackground="#252544")
        style.map('Treeview', background=[('selected', '#3a70d1')])
        
    def update_player_list(self, players):
        # Clear the current list
        for item in self.player_tree.get_children():
            self.player_tree.delete(item)
        
        # Add all players from the list
        for player in players:
            self.player_tree.insert('', tk.END, values=(player['id'][:8]+"...", player['name']))
    
    def update_status(self, status_text):
        self.status_label.config(text=status_text)

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
