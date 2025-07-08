import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
from difficulty_window import DifficultyWindow
from spaceship_settings_window import SpaceshipSettingsWindow

class GameManagerWindow:
    """
    Main window for managing the game server and displaying connected players.
    """
    def __init__(self, root: tk.Tk) -> None:
        self.root: tk.Tk = root
        self.game: Any = None  # Will be set later
        self.player_tree: ttk.Treeview = None  # Will be assigned later
        self.status_label: tk.Label = None  # Will be assigned later
        self.play_button: tk.Button = None  # Bouton Play
        self.pause_button: tk.Button = None  # Bouton Pause
        self.game_running: bool = False  # État du jeu
        
        self.root.title("Pilot Together - Game Manager")
        self.root.geometry("500x400")
        self.root.configure(bg="#1a1a2e")
        
        # Create header
        header_frame: tk.Frame = tk.Frame(root, bg="#1a1a2e")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label: tk.Label = tk.Label(header_frame, text="Game Manager", 
                              font=("Arial", 16, "bold"), 
                              bg="#1a1a2e", fg="#7ab5ff")
        title_label.pack(side=tk.LEFT)

        # Add buttons frame on the right
        buttons_frame: tk.Frame = tk.Frame(header_frame, bg="#1a1a2e")
        buttons_frame.pack(side=tk.RIGHT)

        # Add spaceship button
        spaceship_button: tk.Button = tk.Button(buttons_frame, text="Vaisseau", 
                                     command=self.open_spaceship_settings,
                                     bg="#3a70d1", fg="white", padx=10)
        spaceship_button.pack(side=tk.LEFT, padx=5)

        # Add difficulty button
        difficulty_button: tk.Button = tk.Button(buttons_frame, text="Difficulté", 
                                     command=self.open_difficulty_settings,
                                     bg="#3a70d1", fg="white", padx=10)
        difficulty_button.pack(side=tk.LEFT, padx=5)
        
        # Ajouter les boutons de contrôle du jeu
        control_frame: tk.Frame = tk.Frame(root, bg="#1a1a2e")
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.play_button = tk.Button(control_frame, text="▶ Play", 
                                 command=self.start_game,
                                 bg="#27ae60", fg="white", padx=20, font=("Arial", 10, "bold"))
        self.play_button.pack(side=tk.LEFT, padx=10)
        
        self.pause_button = tk.Button(control_frame, text="⏸ Pause", 
                                  command=self.pause_game,
                                  bg="#3498db", fg="white", padx=20, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT)
        
        # Create player list frame
        player_frame: tk.Frame = tk.Frame(root, bg="#252544")
        player_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        player_header: tk.Label = tk.Label(player_frame, text="Connected Players", 
                              font=("Arial", 12), bg="#252544", fg="#eee")
        player_header.pack(pady=5)
        
        # Create Treeview for player list
        self.player_tree = ttk.Treeview(player_frame, columns=("ID", "Name"), show="headings")
        self.player_tree.heading("ID", text="ID")
        self.player_tree.heading("Name", text="Player Name")
        self.player_tree.column("ID", width=150)
        self.player_tree.column("Name", width=250)
        self.player_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create status bar
        status_frame: tk.Frame = tk.Frame(root, bg="#1a1a2e")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Server starting...", 
                                   bg="#1a1a2e", fg="#eee")
        self.status_label.pack(side=tk.LEFT)
        
        # Configure style for Treeview
        style: ttk.Style = ttk.Style()
        style.configure("Treeview", 
                      background="#252544", 
                      foreground="#eee", 
                      fieldbackground="#252544")
        style.map('Treeview', background=[('selected', '#3a70d1')])
        
    def set_game(self, game: Any) -> None:
        """Set the reference to the game instance."""
        self.game = game
        
    def update_player_list(self, players: List[Dict[str, Any]]) -> None:
        """Update the player list display with current players."""
        # Clear the current list
        for item in self.player_tree.get_children():
            self.player_tree.delete(item)
        
        # Add all players from the list
        for player in players:
            self.player_tree.insert('', tk.END, values=(player['id'][:8]+"...", player['name']))
    
    def update_status(self, status_text: str) -> None:
        """Update the status text in the status bar."""
        self.status_label.config(text=status_text)
    
    def open_difficulty_settings(self) -> None:
        """Open the difficulty settings window."""
        if self.game:
            DifficultyWindow(self.root, self.game)
    
    def open_spaceship_settings(self) -> None:
        """Open the spaceship settings window."""
        if self.game:
            SpaceshipSettingsWindow(self.root, self.game)
    
    def start_game(self) -> None:
        """Start the game when Play button is pressed."""
        if self.game:
            if not self.game_running:
                self.game.start()
                self.game_running = True
                self.play_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.NORMAL, text="⏸ Pause")
                self.update_status("Game started!")
            else:
                self.game.resume()
                self.play_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.NORMAL, text="⏸ Pause")
                self.update_status("Game resumed!")
    
    def pause_game(self) -> None:
        """Pause the game when Pause button is pressed."""
        if self.game and self.game_running:
            self.game.pause()
            self.play_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL, text="⏸ Paused")
            self.update_status("Game paused!")
