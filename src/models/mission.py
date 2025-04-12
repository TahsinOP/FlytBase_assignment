from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Waypoint:
    """Represents a single waypoint in a drone's mission."""
    x: float  # x-coordinate
    y: float  # y-coordinate
    z: Optional[float] = None  # altitude (optional for 3D)
    timestamp: Optional[datetime] = None  # time at which the drone should reach this waypoint

    def __post_init__(self):
        """Validate waypoint coordinates."""
        if self.x < 0 or self.y < 0:
            raise ValueError("Coordinates cannot be negative")
        if self.z is not None and self.z < 0:
            raise ValueError("Altitude cannot be negative")

@dataclass
class Mission:
    """Represents a complete drone mission with waypoints and time window."""
    waypoints: List[Waypoint]
    start_time: datetime
    end_time: datetime
    drone_id: str  # Unique identifier for the drone

    def __post_init__(self):
        """Validate mission parameters."""
        if not self.waypoints:
            raise ValueError("Mission must have at least one waypoint")
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        
        # Sort waypoints by timestamp if they have timestamps
        if all(wp.timestamp is not None for wp in self.waypoints):
            self.waypoints.sort(key=lambda wp: wp.timestamp)
            
        # Validate waypoint timestamps are within mission window
        for wp in self.waypoints:
            if wp.timestamp is not None:
                if not (self.start_time <= wp.timestamp <= self.end_time):
                    raise ValueError("Waypoint timestamp must be within mission time window") 