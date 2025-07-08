class Overheat:
    """
    Gère la surchauffe : accumulation de chaleur, blocage des tirs et refroidissement.
    """
    def __init__(self,
                 max_temp: float = 100.0,
                 heat_per_action: float = 3.0,
                 cool_rate: float = 30.0):
        self.max_temp = max_temp
        self.temperature = 0.0
        self.heat_per_action = heat_per_action
        self.cool_rate = cool_rate
        self.is_cooling = False

    def add_heat(self, heat_value:float = None):
        if heat_value is None:
            heat_value = self.heat_per_action

        self.temperature += heat_value
        if self.temperature >= self.max_temp:
            self.temperature = self.max_temp

    def cool_down(self, delta_time: float):
        """
        Cool down the overheat condition based on the time elapsed.
        
        Args:
            delta_time (float): Time elapsed since last update in seconds
        """
        rate = self.cool_rate * delta_time
        self.temperature = max(0.0, self.temperature - rate)
        self.is_cooling = True

    def stop_cooling(self):
        """
        Stop the cooling process.
        """
        self.is_cooling = False

    def is_overheat(self)-> bool:
        """
        Check if the overheat condition is active.
        
        Returns:
            bool: True if overheated, False otherwise
        """
        return self.temperature >= self.max_temp

    def can_act(self) -> bool:
        """
        Check if actions can be performed (not overheated).
        and if cooling is not in progress.
        
        Returns:
            bool: True if actions can be performed, False if overheated
        """
        return not self.is_overheat() and not self.is_cooling
