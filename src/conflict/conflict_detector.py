from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from models.mission import Mission, Waypoint

@dataclass
class Conflict:
    """Class to store conflict information."""
    location: Tuple[float, float]  # (x, y) coordinates of conflict
    time: datetime  # Time of conflict
    primary_drone: str  # ID of primary drone
    conflicting_drone: str  # ID of conflicting drone
    distance: float  # Distance between drones at conflict point
    description: str  # Human-readable description of the conflict

class ConflictDetector:
    """Class to detect conflicts between drone missions."""
    
    def __init__(self, safety_buffer: float = 50.0):
        """
        Initialize the conflict detector.
        
        Args:
            safety_buffer: Minimum safe distance between drones in meters
        """
        self.safety_buffer = safety_buffer
    
    def check_mission(self, primary_mission: Mission, other_missions: List[Mission]) -> Tuple[str, List[Conflict]]:
        """
        Check for conflicts between primary mission and other missions.
        
        Args:
            primary_mission: The primary drone's mission
            other_missions: List of other drone missions
            
        Returns:
            Tuple of (status, conflicts)
            - status: "clear" or "conflict detected"
            - conflicts: List of Conflict objects describing detected conflicts
        """
        conflicts = []
        
        # Check each other mission against the primary mission
        for other_mission in other_missions:
            mission_conflicts = self._check_mission_pair(primary_mission, other_mission)
            conflicts.extend(mission_conflicts)
        
        if conflicts:
            return "conflict detected", conflicts
        return "clear", []
    
    def _check_mission_pair(self, mission1: Mission, mission2: Mission) -> List[Conflict]:
        """
        Check for conflicts between two missions.
        
        Args:
            mission1: First mission
            mission2: Second mission
            
        Returns:
            List of Conflict objects describing detected conflicts
        """
        conflicts = []
        
        # Get all waypoint pairs that could potentially conflict
        for i in range(len(mission1.waypoints) - 1):
            for j in range(len(mission2.waypoints) - 1):
                wp1_start = mission1.waypoints[i]
                wp1_end = mission1.waypoints[i + 1]
                wp2_start = mission2.waypoints[j]
                wp2_end = mission2.waypoints[j + 1]
                
                # Check if time windows overlap
                if self._check_temporal_overlap(wp1_start, wp1_end, wp2_start, wp2_end):
                    # Check for spatial conflict
                    conflict_point = self._find_intersection(
                        wp1_start, wp1_end, wp2_start, wp2_end
                    )
                    
                    if conflict_point:
                        conflict_time = self._calculate_conflict_time(
                            wp1_start, wp1_end, wp2_start, wp2_end, conflict_point
                        )
                        
                        if conflict_time:
                            distance = self._calculate_distance(
                                wp1_start, wp2_start, conflict_point
                            )
                            
                            if distance < self.safety_buffer:
                                conflicts.append(Conflict(
                                    location=conflict_point,
                                    time=conflict_time,
                                    primary_drone=mission1.drone_id,
                                    conflicting_drone=mission2.drone_id,
                                    distance=distance,
                                    description=f"Conflict between {mission1.drone_id} and {mission2.drone_id} "
                                              f"at ({conflict_point[0]:.2f}, {conflict_point[1]:.2f}) "
                                              f"at time {conflict_time.strftime('%H:%M:%S')} "
                                              f"with distance {distance:.2f}m"
                                ))
        
        return conflicts
    
    def _check_temporal_overlap(self, 
                              wp1_start: Waypoint, wp1_end: Waypoint,
                              wp2_start: Waypoint, wp2_end: Waypoint) -> bool:
        """Check if two time windows overlap."""
        return not (wp1_end.timestamp < wp2_start.timestamp or 
                   wp2_end.timestamp < wp1_start.timestamp)
    
    def _find_intersection(self, 
                         wp1_start: Waypoint, wp1_end: Waypoint,
                         wp2_start: Waypoint, wp2_end: Waypoint) -> Optional[Tuple[float, float]]:
        """Find intersection point between two line segments."""
        # Convert waypoints to line segments
        p1 = np.array([wp1_start.x, wp1_start.y])
        p2 = np.array([wp1_end.x, wp1_end.y])
        p3 = np.array([wp2_start.x, wp2_start.y])
        p4 = np.array([wp2_end.x, wp2_end.y])
        
        # Calculate intersection
        denominator = (p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0])
        
        if denominator == 0:  # Lines are parallel
            return None
            
        t = ((p1[0] - p3[0]) * (p3[1] - p4[1]) - (p1[1] - p3[1]) * (p3[0] - p4[0])) / denominator
        u = -((p1[0] - p2[0]) * (p1[1] - p3[1]) - (p1[1] - p2[1]) * (p1[0] - p3[0])) / denominator
        
        # Check if intersection is within both line segments
        if 0 <= t <= 1 and 0 <= u <= 1:
            intersection = p1 + t * (p2 - p1)
            return (float(intersection[0]), float(intersection[1]))
        
        return None
    
    def _calculate_conflict_time(self,
                               wp1_start: Waypoint, wp1_end: Waypoint,
                               wp2_start: Waypoint, wp2_end: Waypoint,
                               intersection: Tuple[float, float]) -> Optional[datetime]:
        """Calculate the time at which the conflict occurs."""
        # Calculate time based on distance along the path
        total_dist1 = np.sqrt((wp1_end.x - wp1_start.x)**2 + (wp1_end.y - wp1_start.y)**2)
        dist_to_conflict1 = np.sqrt((intersection[0] - wp1_start.x)**2 + (intersection[1] - wp1_start.y)**2)
        time_ratio1 = dist_to_conflict1 / total_dist1 if total_dist1 > 0 else 0
        
        time_diff1 = (wp1_end.timestamp - wp1_start.timestamp).total_seconds()
        conflict_time = wp1_start.timestamp + timedelta(seconds=time_ratio1 * time_diff1)
        
        return conflict_time
    
    def _calculate_distance(self, wp1: Waypoint, wp2: Waypoint, point: Tuple[float, float]) -> float:
        """Calculate distance between two points."""
        return np.sqrt((wp1.x - wp2.x)**2 + (wp1.y - wp2.y)**2) 