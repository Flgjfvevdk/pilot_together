import tkinter as tk
import logging
import math
from typing import Optional, Any, Union

class DifficultyWindow:
    """
    Window for adjusting game difficulty settings.
    """
    # Constantes pour les valeurs limites
    MIN_INTERVAL: float = 0.01
    MAX_INTERVAL: float = 5.0
    DEFAULT_INTERVAL: float = 0.5
    
    def __init__(self, parent: tk.Tk, game_instance: Any) -> None:
        self.game: Any = game_instance
        self.parent: tk.Tk = parent
        self.adversity: Optional[Any] = None
        self.spawn_interval: float = self.DEFAULT_INTERVAL
        self.window: tk.Toplevel = tk.Toplevel(parent)
        self.value_var: tk.StringVar = tk.StringVar(value=str(self.spawn_interval))
        self.entry: tk.Entry = None  # Will be assigned later
        self.slider: tk.Scale = None  # Will be assigned later
        
        # Create the window
        self.window.title("Paramètres de Difficulté")
        self.window.geometry("400x250")  # Légèrement plus grand pour accommoder les nouvelles options
        self.window.configure(bg="#1a1a2e")
        self.window.resizable(False, False)
        self.window.transient(parent)  # Set as a transient window to parent
        self.window.grab_set()  # Make this window modal
        
        # Get the current spawn interval from the adversity object
        self.find_adversity()
        
        # Frame for content
        content_frame: tk.Frame = tk.Frame(self.window, bg="#1a1a2e")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Label for section
        tk.Label(content_frame, text="Fréquence de spawn des astéroïdes", 
                 font=("Arial", 12), bg="#1a1a2e", fg="white").pack(pady=5)
        
        # Entry box for direct input
        entry_frame: tk.Frame = tk.Frame(content_frame, bg="#1a1a2e")
        entry_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(entry_frame, text="Intervalle (secondes):", 
                 bg="#1a1a2e", fg="white").pack(side=tk.LEFT)
        
        self.entry = tk.Entry(entry_frame, textvariable=self.value_var, width=10)
        self.entry.pack(side=tk.LEFT, padx=10)
        self.entry.bind("<Return>", self.update_from_entry)
        
        # Info about values
        info_label = tk.Label(content_frame, 
                             text=f"Note: Réglez à 0 pour désactiver, ou utilisez des valeurs de {self.MIN_INTERVAL} à {self.MAX_INTERVAL}",
                             bg="#1a1a2e", fg="#aaaaaa", font=("Arial", 8))
        info_label.pack(pady=2)
        
        # Slider with logarithmic scale (internally 0-100, transformed to MIN-MAX)
        self.slider = tk.Scale(content_frame, 
                             from_=0, to=100,  # Internal scale
                             resolution=1,
                             orient=tk.HORIZONTAL,
                             label="Désactivé (0) | Rapide ← → Lent",
                             length=300,
                             bg="#252544",
                             fg="white",
                             highlightthickness=0,
                             troughcolor="#0a0a18",
                             activebackground="#3a70d1",
                             command=self.update_from_slider)
        
        # Set initial slider position from spawn_interval
        self.set_slider_from_value(self.spawn_interval)
        self.slider.pack(fill=tk.X, pady=10)
        
        # Button frame
        button_frame: tk.Frame = tk.Frame(content_frame, bg="#1a1a2e")
        button_frame.pack(fill=tk.X, pady=10)
        
        # Special buttons
        tk.Button(button_frame, text="Désactiver", command=self.disable_spawn,
                 bg="#b53a3a", fg="white", padx=10).pack(side=tk.LEFT)
                 
        tk.Button(button_frame, text=f"Normal ({self.DEFAULT_INTERVAL}s)", 
                 command=lambda: self.set_preset(self.DEFAULT_INTERVAL),
                 bg="#3a70d1", fg="white", padx=10).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text=f"Lent ({self.MAX_INTERVAL/2.5:.1f}s)", 
                 command=lambda: self.set_preset(self.MAX_INTERVAL/2.5),
                 bg="#3a70d1", fg="white", padx=10).pack(side=tk.LEFT, padx=0)
        
        # Close button
        tk.Button(button_frame, text="Fermer", command=self.window.destroy,
                 bg="#3a70d1", fg="white", padx=20).pack(side=tk.RIGHT)
    
    def find_adversity(self) -> None:
        """Find the adversity manager in the game objects."""
        self.adversity = None
        self.spawn_interval = self.DEFAULT_INTERVAL  # Default value
        
        # Look for the adversity object to get its current spawn interval
        for obj_id, obj in self.game.game_objects.items():
            if obj_id == "adversity_manager":
                self.adversity = obj
                self.spawn_interval = obj.spawn_interval
                break
    
    def update_from_slider(self, slider_pos: str) -> None:
        """Convert slider position to actual value using logarithmic scale"""
        try:
            slider_pos_float: float = float(slider_pos)
            
            # Special case: 0 = disabled
            if slider_pos_float == 0:
                value: float = 0
            else:
                # Transform slider position (1-100) to value
                # For a nice logarithmic scale: 1 maps to MIN, 100 maps to MAX
                # Normalize slider to 0-1 range (excluding 0 position)
                normalized: float = (slider_pos_float - 1) / 99.0
                # Apply logarithmic transformation
                value = self.MIN_INTERVAL * math.pow(self.MAX_INTERVAL/self.MIN_INTERVAL, normalized)
                value = round(value, 2)  # Round to 2 decimal places
                
            self.value_var.set(f"{value:.2f}")
            self.update_game_value(value)
        except ValueError:
            pass
    
    def set_slider_from_value(self, value: float) -> None:
        """Convert actual value to slider position using logarithmic scale"""
        if value <= 0:
            # Special case: disabled
            self.slider.set(0)
        else:
            # Ensure value is within bounds
            value_clamped: float = max(self.MIN_INTERVAL, min(self.MAX_INTERVAL, value))
            
            # Transform value to slider position (1-100)
            # Calculate logarithmic position
            normalized: float = 0
            if value_clamped >= self.MIN_INTERVAL:
                normalized = math.log(value_clamped / self.MIN_INTERVAL) / math.log(self.MAX_INTERVAL / self.MIN_INTERVAL)
            
            # Map to slider range (1-100)
            slider_pos: float = 1 + normalized * 99
            self.slider.set(int(slider_pos))
    
    def update_from_entry(self, event: Optional[tk.Event] = None) -> None:
        """Update the slider and game value when entry changes."""
        try:
            value: float = float(self.value_var.get())
            # Clamp to min/max values (allowing 0)
            value = max(0, min(self.MAX_INTERVAL, value))
            # Round to 2 decimal places
            value = round(value, 2)
            # Update the slider
            self.set_slider_from_value(value)
            # Update the game
            self.update_game_value(value)
        except ValueError:
            # Reset to current value if entry is invalid
            self.value_var.set(f"{self.spawn_interval:.2f}")
    
    def disable_spawn(self) -> None:
        """Convenience method to disable asteroid spawning."""
        self.slider.set(0)
        self.value_var.set("0.00")
        self.update_game_value(0)
    
    def set_preset(self, value: float) -> None:
        """Set a preset difficulty value."""
        value_rounded: float = round(value, 2)
        self.value_var.set(f"{value_rounded:.2f}")
        self.set_slider_from_value(value_rounded)
        self.update_game_value(value_rounded)
    
    def update_game_value(self, value: float) -> None:
        """Update the spawn interval in the game."""
        if self.adversity:
            self.adversity.spawn_interval = value
            self.spawn_interval = value
            
            # Log the change with special message for disabled
            if value == 0:
                logging.info("Asteroid spawning disabled")
            else:
                logging.info(f"Updated asteroid spawn interval to {value:.2f} seconds")
