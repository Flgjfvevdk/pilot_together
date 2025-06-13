import math
from vector import Vector
from typing import List, Dict, Tuple, Optional

class Collider:
    """
    Defines a collider for game objects to enable collision detection.
    Currently implements a rotatable rectangle collider.
    """
    
    def __init__(self, width: float = 0, height: float = 0, offset_x: float = 0, offset_y: float = 0, angle: float = 0):
        """
        Initialize a new Collider.
        
        Args:
            width (float): Width of the collider
            height (float): Height of the collider
            offset_x (float): X offset from the object's position
            offset_y (float): Y offset from the object's position
            angle (float): Rotation angle in radians
        """
        self.width: float = width
        self.height: float = height
        self.offset: Vector = Vector(offset_x, offset_y)
        self.angle: float = angle  # Rotation in radians
        
    def get_corners(self, position: Vector) -> List[Vector]:
        """
        Get the four corners of the collider based on a given position.
        
        Args:
            position (Vector): The position of the game object
            
        Returns:
            list: Four Vector objects representing the corners
        """
        # Calculate the center of the collider
        center: Vector = position + self.offset
        
        # Calculate the four corners relative to the center (before rotation)
        half_w: float = self.width / 2
        half_h: float = self.height / 2
        corners: List[Vector] = [
            Vector(-half_w, -half_h),  # Top-left
            Vector(half_w, -half_h),   # Top-right
            Vector(half_w, half_h),    # Bottom-right
            Vector(-half_w, half_h)    # Bottom-left
        ]
        
        # Apply rotation to each corner and translate to world position
        rotated_corners: List[Vector] = []
        for corner in corners:
            rotated: Vector = corner.rotate(self.angle)
            world_corner: Vector = center + rotated
            rotated_corners.append(world_corner)
            
        return rotated_corners
    
    def intersects(self, other: 'Collider', my_pos: Vector, other_pos: Vector) -> bool:
        """
        Check if this collider intersects with another collider.
        Uses the Separating Axis Theorem (SAT) for rotated rectangles.
        
        Args:
            other (Collider): The other collider to check against
            my_pos (Vector): Position of this game object
            other_pos (Vector): Position of the other game object
            
        Returns:
            bool: True if colliders intersect, False otherwise
        """
        # If either collider has zero size, no collision
        if self.width == 0 or self.height == 0 or other.width == 0 or other.height == 0:
            return False
            
        # Get the corners of both colliders
        corners_a: List[Vector] = self.get_corners(my_pos)
        corners_b: List[Vector] = other.get_corners(other_pos)
        
        # Get the axes to test (perpendicular to each side)
        axes: List[Vector] = []
        
        # Axes from this collider
        for i in range(len(corners_a)):
            edge: Vector = corners_a[(i + 1) % len(corners_a)] - corners_a[i]
            normal: Vector = Vector(-edge.y, edge.x).normalize()
            axes.append(normal)
            
        # Axes from other collider
        for i in range(len(corners_b)):
            edge: Vector = corners_b[(i + 1) % len(corners_b)] - corners_b[i]
            normal: Vector = Vector(-edge.y, edge.x).normalize()
            axes.append(normal)
        
        # Test projection overlap on each axis
        for axis in axes:
            # Project both colliders onto the axis
            min_a: float = float('inf')
            max_a: float = float('-inf')
            min_b: float = float('inf')
            max_b: float = float('-inf')
            
            # Project first collider
            for corner in corners_a:
                projection: float = axis.dot(corner)
                min_a = min(min_a, projection)
                max_a = max(max_a, projection)
                
            # Project second collider
            for corner in corners_b:
                projection: float = axis.dot(corner)
                min_b = min(min_b, projection)
                max_b = max(max_b, projection)
            
            # Check for overlap
            if max_a < min_b or max_b < min_a:
                # Found a separating axis, no collision
                return False
        
        # No separating axis found, objects collide
        return True
    
    def contains_point(self, point: Vector, position: Vector) -> bool:
        """
        Check if a point is inside the collider.
        
        Args:
            point (Vector): The point to check
            position (Vector): The position of the game object
            
        Returns:
            bool: True if the point is inside the collider, False otherwise
        """
        # Get corners
        corners: List[Vector] = self.get_corners(position)
        
        # For each edge of the polygon
        for i in range(len(corners)):
            edge: Vector = corners[(i + 1) % len(corners)] - corners[i]
            # Vector from corner to point
            to_point: Vector = point - corners[i]
            
            # Cross product will be negative if point is to the right of the edge
            if edge.x * to_point.y - edge.y * to_point.x < 0:
                return False
                
        return True
    
    def to_dict(self) -> Dict:
        """
        Convert the collider to a dictionary for serialization.
        
        Returns:
            dict: Collider properties
        """
        return {
            'width': self.width,
            'height': self.height,
            'offsetX': self.offset.x,
            'offsetY': self.offset.y,
            'angle': self.angle
        }
