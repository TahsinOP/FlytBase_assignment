from data.data_loader import DataLoader
from models.mission import Mission, Waypoint
from datetime import datetime, timedelta
import os

def test_mission_creation():
    """Test creating a mission with waypoints."""
    # Create a simple mission
    waypoints = [
        Waypoint(x=0, y=0, z=10),
        Waypoint(x=100, y=100, z=20),
        Waypoint(x=200, y=0, z=15)
    ]
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=1)
    
    mission = Mission(
        waypoints=waypoints,
        start_time=start_time,
        end_time=end_time,
        drone_id="test_drone"
    )
    
    print("Mission created successfully:")
    print(f"Drone ID: {mission.drone_id}")
    print(f"Time window: {mission.start_time} to {mission.end_time}")
    print("Waypoints:")
    for i, wp in enumerate(mission.waypoints):
        print(f"  {i+1}. ({wp.x}, {wp.y}, {wp.z})")

def test_sample_data():
    """Test loading sample mission data."""
    missions = DataLoader.create_sample_data()
    
    print("\nPrimary Mission:")
    print(f"Drone ID: {missions['primary'].drone_id}")
    print("Waypoints:")
    for wp in missions['primary'].waypoints:
        print(f"  ({wp.x}, {wp.y}, {wp.z}) at {wp.timestamp}")
    
    print("\nOther Missions:")
    for mission in missions['others']:
        print(f"\nDrone ID: {mission.drone_id}")
        print("Waypoints:")
        for wp in mission.waypoints:
            print(f"  ({wp.x}, {wp.y}, {wp.z}) at {wp.timestamp}")

def test_json_loading():
    """Test loading mission data from JSON file."""
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_mission.json')
    missions = DataLoader.load_from_json(json_path)
    
    print("\nLoading from JSON file:")
    print("\nPrimary Mission:")
    print(f"Drone ID: {missions['primary'].drone_id}")
    print("Waypoints:")
    for wp in missions['primary'].waypoints:
        print(f"  ({wp.x}, {wp.y}, {wp.z}) at {wp.timestamp}")
    
    print("\nOther Missions:")
    for mission in missions['others']:
        print(f"\nDrone ID: {mission.drone_id}")
        print("Waypoints:")
        for wp in mission.waypoints:
            print(f"  ({wp.x}, {wp.y}, {wp.z}) at {wp.timestamp}")

def test_generated_data():
    """Test generating mission data with custom parameters."""
    print("\nGenerating mission data with custom parameters:")
    missions = DataLoader.generate_mission_data(
        num_traffic_drones=4,
        waypoints_per_drone=10,
        area_size=1000.0,
        min_altitude=10.0,
        max_altitude=100.0,
        mission_duration=timedelta(hours=1),
        time_buffer=timedelta(minutes=15)
    )
    
    print("\nPrimary Mission:")
    print(f"Drone ID: {missions['primary'].drone_id}")
    print(f"Number of waypoints: {len(missions['primary'].waypoints)}")
    print(f"Time window: {missions['primary'].start_time} to {missions['primary'].end_time}")
    
    print("\nTraffic Drones:")
    for mission in missions['others']:
        print(f"\nDrone ID: {mission.drone_id}")
        print(f"Number of waypoints: {len(mission.waypoints)}")
        print(f"Time window: {mission.start_time} to {mission.end_time}")

if __name__ == "__main__":
    # print("Testing Mission Creation:")
    # test_mission_creation()
    
    print("\nTesting Sample Data:")
    test_sample_data()
    
    print("\nTesting JSON Loading:")
    test_json_loading()
    
    print("\nTesting Generated Data:")
    test_generated_data() 