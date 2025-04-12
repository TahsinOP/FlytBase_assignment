import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import random

from models.mission import Waypoint, Mission

class DataLoader:
    """Handles loading of mission data from different sources."""
    
    @staticmethod
    def load_from_json(file_path: str) -> Dict[str, Mission]:
        """Load mission data from a JSON file.
        
        Expected JSON format:
        {
            "primary_mission": {
                "drone_id": "drone1",
                "start_time": "2024-04-10T10:00:00",
                "end_time": "2024-04-10T11:00:00",
                "waypoints": [
                    {"x": 0, "y": 0, "z": 10, "timestamp": "2024-04-10T10:00:00"},
                    {"x": 100, "y": 100, "z": 20, "timestamp": "2024-04-10T10:30:00"}
                ]
            },
            "other_missions": [
                {
                    "drone_id": "drone2",
                    "start_time": "2024-04-10T10:15:00",
                    "end_time": "2024-04-10T11:15:00",
                    "waypoints": [...]
                }
            ]
        }
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        missions = {}
        
        # Load primary mission
        primary_data = data['primary_mission']
        missions['primary'] = DataLoader._create_mission(primary_data)
        
        # Load other missions
        missions['others'] = [
            DataLoader._create_mission(mission_data)
            for mission_data in data['other_missions']
        ]
        
        return missions
    
    @staticmethod
    def _create_mission(data: Dict[str, Any]) -> Mission:
        """Create a Mission object from dictionary data."""
        waypoints = [
            Waypoint(
                x=wp['x'],
                y=wp['y'],
                z=wp.get('z'),
                timestamp=datetime.fromisoformat(wp['timestamp']) if 'timestamp' in wp else None
            )
            for wp in data['waypoints']
        ]
        
        return Mission(
            waypoints=waypoints,
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            drone_id=data['drone_id']
        )
    
    @staticmethod
    def generate_mission_data(
        num_traffic_drones: int = 4,
        waypoints_per_drone: int = 10,
        area_size: float = 1000.0,  # Size of the operational area in meters
        min_altitude: float = 10.0,  # Minimum altitude in meters
        max_altitude: float = 100.0,  # Maximum altitude in meters
        mission_duration: timedelta = timedelta(hours=1),
        time_buffer: timedelta = timedelta(minutes=15)  # Buffer between drone missions
    ) -> Dict[str, Mission]:
        """Generate mission data with configurable parameters.
        
        Args:
            num_traffic_drones: Number of traffic drones to generate
            waypoints_per_drone: Number of waypoints per drone
            area_size: Size of the operational area in meters
            min_altitude: Minimum altitude in meters
            max_altitude: Maximum altitude in meters
            mission_duration: Duration of each mission
            time_buffer: Minimum time buffer between drone missions
            
        Returns:
            Dictionary containing primary mission and other missions
        """
        now = datetime.now()
        
        # Generate primary mission
        primary_mission = DataLoader._generate_drone_mission(
            drone_id="primary_drone",
            start_time=now,
            duration=mission_duration,
            area_size=area_size,
            min_altitude=min_altitude,
            max_altitude=max_altitude,
            num_waypoints=waypoints_per_drone
        )
        
        # Generate traffic drone missions
        other_missions = []
        for i in range(num_traffic_drones):
            # Stagger start times to avoid all drones starting at once
            start_time = now + time_buffer * (i + 1)
            mission = DataLoader._generate_drone_mission(
                drone_id=f"traffic_drone_{i+1}",
                start_time=start_time,
                duration=mission_duration,
                area_size=area_size,
                min_altitude=min_altitude,
                max_altitude=max_altitude,
                num_waypoints=waypoints_per_drone
            )
            other_missions.append(mission)
        
        return {
            'primary': primary_mission,
            'others': other_missions
        }
    
    @staticmethod
    def _generate_drone_mission(
        drone_id: str,
        start_time: datetime,
        duration: timedelta,
        area_size: float,
        min_altitude: float,
        max_altitude: float,
        num_waypoints: int
    ) -> Mission:
        """Generate a single drone mission with random waypoints."""
        end_time = start_time + duration
        time_step = duration / (num_waypoints - 1)
        
        waypoints = []
        for i in range(num_waypoints):
            # Generate random coordinates within the area
            x = random.uniform(0, area_size)
            y = random.uniform(0, area_size)
            z = random.uniform(min_altitude, max_altitude)
            
            # Calculate timestamp for this waypoint
            timestamp = start_time + time_step * i
            
            waypoints.append(Waypoint(
                x=x,
                y=y,
                z=z,
                timestamp=timestamp
            ))
        
        return Mission(
            waypoints=waypoints,
            start_time=start_time,
            end_time=end_time,
            drone_id=drone_id
        )
    
    @staticmethod
    def create_sample_data() -> Dict[str, Mission]:
        """Create sample mission data for testing."""
        return DataLoader.generate_mission_data(
            num_traffic_drones=2,
            waypoints_per_drone=3,
            area_size=300.0,
            min_altitude=10.0,
            max_altitude=30.0,
            mission_duration=timedelta(hours=1),
            time_buffer=timedelta(minutes=15)
        ) 