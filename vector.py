import math

class Vector:
    """
    A 2D vector class for game physics and movement calculations.
    Handles vector operations like addition, subtraction, scaling, etc.
    """
    
    def __init__(self, x=0.0, y=0.0):
        """
        Initialize a new Vector.
        
        Args:
            x (float): X component
            y (float): Y component
        """
        self.x = float(x)
        self.y = float(y)
    
    def __str__(self):
        """String representation of the vector."""
        return f"Vector({self.x:.2f}, {self.y:.2f})"
    
    def __repr__(self):
        """Detailed string representation of the vector."""
        return f"Vector(x={self.x}, y={self.y})"
    
    def __eq__(self, other):
        """Check if two vectors are equal."""
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return False
    
    def __add__(self, other):
        """Add two vectors."""
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        raise TypeError("Can only add Vector objects")
    
    def __sub__(self, other):
        """Subtract two vectors."""
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        raise TypeError("Can only subtract Vector objects")
    
    def __mul__(self, scalar):
        """Multiply vector by scalar."""
        return Vector(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):
        """Right multiplication for scalar * vector."""
        return self.__mul__(scalar)
    
    def __neg__(self):
        """Return the negative of this vector."""
        return Vector(-self.x, -self.y)
    
    def __truediv__(self, scalar):
        """Divide vector by scalar."""
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        return Vector(self.x / scalar, self.y / scalar)
    
    def magnitude(self):
        """Calculate the magnitude (length) of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def magnitude_squared(self):
        """Calculate the squared magnitude of the vector.
        This is faster than magnitude() when comparing distances.
        """
        return self.x * self.x + self.y * self.y
    
    def normalize(self):
        """Return a normalized unit vector in the same direction."""
        mag = self.magnitude()
        if mag == 0:
            return Vector(0, 0)
        return Vector(self.x / mag, self.y / mag)
    
    def dot(self, other):
        """Calculate the dot product with another vector."""
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        raise TypeError("Can only calculate dot product with Vector objects")
    
    def distance_to(self, other):
        """Calculate the distance to another vector."""
        if isinstance(other, Vector):
            return (other - self).magnitude()
        raise TypeError("Can only calculate distance to Vector objects")
    
    def angle(self):
        """Calculate the angle in radians of this vector from the positive x-axis."""
        return math.atan2(self.y, self.x)
    
    def angle_between(self, other):
        """Calculate the angle between this vector and another vector."""
        if isinstance(other, Vector):
            dot = self.normalize().dot(other.normalize())
            # Clamp dot product to [-1, 1] to handle floating point errors
            dot = max(-1.0, min(1.0, dot))
            return math.acos(dot)
        raise TypeError("Can only calculate angle between Vector objects")
    
    def rotate(self, angle):
        """Rotate the vector by the given angle in radians."""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x = self.x * cos_a - self.y * sin_a
        y = self.x * sin_a + self.y * cos_a
        return Vector(x, y)
    
    def as_tuple(self):
        """Return the vector as a tuple of (x, y)."""
        return (self.x, self.y)
    
    def copy(self):
        """Return a copy of this vector."""
        return Vector(self.x, self.y)
    
    @staticmethod
    def from_angle(angle, magnitude=1.0):
        """Create a vector from an angle and magnitude."""
        return Vector(math.cos(angle) * magnitude, math.sin(angle) * magnitude)
    
    @staticmethod
    def from_direction(direction, magnitude=1.0):
        """Create a vector from a direction str and magnitude."""
        for dir_name, dir_vector in {
            'up': Vector(0, -1),
            'down': Vector(0, 1),
            'left': Vector(-1, 0),
            'right': Vector(1, 0)
        }.items():
            if direction == dir_name:
                return dir_vector * magnitude
        raise ValueError(f"Invalid direction: {direction}. Must be one of 'up', 'down', 'left', 'right'.")
