import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
from difficulty_window import DifficultyWindow

class GameManagerWindow:
    """
    Main window for managing the game server and displaying connected players.
    """
    def __init__(self, root: tk.Tk) -> None:
        self.root: tk.Tk = root
        self.game: Any = None  # Will be set later
        self.player_tree: ttk.Treeview = None  # Will be assigned later
        self.status_label: tk.Label = None  # Will be assigned later
        
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

        # Add difficulty button
        difficulty_button: tk.Button = tk.Button(header_frame, text="Difficulté", 
                                     command=self.open_difficulty_settings,
                                     bg="#3a70d1", fg="white", padx=10)
        difficulty_button.pack(side=tk.RIGHT, padx=10)
        
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
