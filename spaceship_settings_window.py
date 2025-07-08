import tkinter as tk
import logging
from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game import Game

class SpaceshipSettingsWindow:
    """
    Window for adjusting spaceship settings.
    """
    def __init__(self, parent: tk.Tk, game_instance: 'Game') -> None:
        self.game = game_instance
        self.parent = parent
        self.spaceship = self.game.spaceship
        self.window = tk.Toplevel(parent)
        
        # Récupérer la valeur actuelle des canons actifs
        self.active_cannons = 4  # Par défaut, tous les canons sont actifs
        
        # Create the window
        self.window.title("Paramètres du Vaisseau")
        self.window.geometry("400x300")
        self.window.configure(bg="#1a1a2e")
        self.window.resizable(False, False)
        self.window.transient(parent)  # Set as a transient window to parent
        self.window.grab_set()  # Make this window modal
        
        # Frame for content
        content_frame = tk.Frame(self.window, bg="#1a1a2e")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Label for section
        tk.Label(content_frame, text="Paramètres des Canons", 
                 font=("Arial", 12), bg="#1a1a2e", fg="white").pack(pady=5)
        
        # Frame for active cannons settings
        cannon_frame = tk.Frame(content_frame, bg="#1a1a2e")
        cannon_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(cannon_frame, text="Nombre de canons actifs:",
                 bg="#1a1a2e", fg="white").pack(side=tk.LEFT)
        
        # Spinbox for selecting number of active cannons
        self.active_cannons_var = tk.IntVar(value=self.active_cannons)
        self.cannons_spinbox = tk.Spinbox(
            cannon_frame,
            from_=0,
            to=4,
            width=5,
            textvariable=self.active_cannons_var,
            command=self.update_active_cannons
        )
        self.cannons_spinbox.pack(side=tk.LEFT, padx=10)
        
        # Description label
        tk.Label(
            content_frame,
            text="Les canons désactivés ne pourront pas être sélectionnés par les joueurs.",
            bg="#1a1a2e", fg="#aaaaaa", font=("Arial", 8), wraplength=360
        ).pack(pady=2)
        
        # Preview of which cannon buttons will be disabled
        self.preview_frame = tk.Frame(content_frame, bg="#252544", padx=10, pady=10)
        self.preview_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            self.preview_frame,
            text="Aperçu des canons:",
            bg="#252544", fg="white"
        ).pack(anchor="w")
        
        # Create button preview
        self.button_frame = tk.Frame(self.preview_frame, bg="#252544")
        self.button_frame.pack(pady=5)
        
        self.cannon_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.button_frame,
                text=str(i+1),
                width=3, height=1,
                bg="#3a70d1" if i < self.active_cannons else "#666666",
                fg="white" if i < self.active_cannons else "#aaaaaa",
                state=tk.NORMAL if i < self.active_cannons else tk.DISABLED
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.cannon_buttons.append(btn)
        
        # Apply button
        apply_button = tk.Button(
            content_frame,
            text="Appliquer",
            command=self.apply_settings,
            bg="#27ae60",
            fg="white",
            padx=10
        )
        apply_button.pack(pady=10)
        
        # Close button
        close_button = tk.Button(
            content_frame,
            text="Fermer",
            command=self.window.destroy,
            bg="#3a70d1",
            fg="white",
            padx=10
        )
        close_button.pack(pady=5)
        
    def update_active_cannons(self) -> None:
        """Update the preview when number of active cannons changes."""
        try:
            # Get value from spinbox
            active_cannons = self.active_cannons_var.get()
            
            # Clamp value to allowed range
            active_cannons = max(0, min(4, active_cannons))
            
            # Update preview buttons
            for i, btn in enumerate(self.cannon_buttons):
                if i < active_cannons:
                    btn.config(
                        bg="#3a70d1",
                        fg="white",
                        state=tk.NORMAL
                    )
                else:
                    btn.config(
                        bg="#666666",
                        fg="#aaaaaa",
                        state=tk.DISABLED
                    )
        except ValueError:
            # Reset to current value if invalid input
            self.active_cannons_var.set(self.active_cannons)
    
    def apply_settings(self) -> None:
        """Apply the settings to the spaceship."""
        try:
            active_cannons = self.active_cannons_var.get()
            
            # Clamp value to allowed range
            active_cannons = max(0, min(4, active_cannons))
            
            # Save the new value
            self.active_cannons = active_cannons
            
            # Apply to spaceship
            if self.spaceship:
                self.spaceship.set_active_cannons(active_cannons)
                logging.info(f"Set active cannons to {active_cannons}")
                
                # Notify clients about the change
                if self.game.socketio:
                    self.game.socketio.emit('update_active_cannons', {'active_cannons': active_cannons})
        except ValueError:
            # Reset to current value if invalid input
            self.active_cannons_var.set(self.active_cannons)
