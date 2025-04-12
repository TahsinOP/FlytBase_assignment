from data.data_loader import DataLoader
from conflict.conflict_detector import ConflictDetector, Conflict
from visualization.plotter import MissionPlotter
from visualization.plotly_plotter import PlotlyMissionPlotter
from datetime import datetime
from models.mission import Mission, Waypoint
from typing import List, Dict
import os
import json

def check_mission_safety(primary_mission: Mission, other_missions: List[Mission], 
                        safety_buffer: float = 50.0) -> Dict:
    """
    Query interface to check mission safety.
    
    Args:
        primary_mission: The primary drone's mission
        other_missions: List of other drone missions
        safety_buffer: Minimum safe distance between drones in meters
        
    Returns:
        Dictionary containing:
        - status: "clear" or "conflict detected"
        - conflicts: List of Conflict objects
        - summary: Human-readable summary of the check
    """
    detector = ConflictDetector(safety_buffer=safety_buffer)
    status, conflicts = detector.check_mission(primary_mission, other_missions)
    
    result = {
        "status": status,
        "conflicts": conflicts,  # Keep the original Conflict objects
        "summary": f"Mission Safety Check with {safety_buffer}m buffer:\n"
    }
    
    if conflicts:
        result["summary"] += f"⚠️ {len(conflicts)} conflicts detected!\n"
        for i, conflict in enumerate(conflicts, 1):
            result["summary"] += f"\nConflict {i}:\n"
            result["summary"] += f"  Location: ({conflict.location[0]:.2f}, {conflict.location[1]:.2f})\n"
            result["summary"] += f"  Time: {conflict.time.strftime('%H:%M:%S')}\n"
            result["summary"] += f"  Distance: {conflict.distance:.2f}m\n"
            result["summary"] += f"  Description: {conflict.description}\n"
    else:
        result["summary"] += "✅ No conflicts detected. Mission is safe to proceed."
    
    return result

def visualize_conflict_scenario():
    """Visualize a scenario with conflicts."""
    # Load test scenarios
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_scenarios.json')
    missions = DataLoader.load_from_json(json_path)
    
    # Check mission safety using the query interface
    safety_check = check_mission_safety(missions['primary'], missions['others'])
    print("\nMission Safety Check Results:")
    print("=" * 50)
    print(safety_check["summary"])
    
    # Initialize plotter
    plotter = MissionPlotter()
    
    # Plot static visualization
    plotter.plot_all_missions(missions, safety_check["conflicts"])
    plotter.save('conflict_visualization.png')
    
    # Create animation (faster with 500ms interval)
    plotter.plot_mission_animation(
        missions,
        safety_check["conflicts"],
        interval=500,  # 0.5 seconds per frame
        save_path='conflict_animation.gif'
    )

def visualize_conflict_free_scenario():
    """Visualize a conflict-free scenario."""
    # Create a conflict-free scenario
    missions = {
        'primary': Mission(
            waypoints=[
                Waypoint(x=0, y=0, timestamp=datetime(2024, 4, 10, 10, 0)),
                Waypoint(x=100, y=0, timestamp=datetime(2024, 4, 10, 10, 5)),
                Waypoint(x=200, y=0, timestamp=datetime(2024, 4, 10, 10, 10)),
            ],
            start_time=datetime(2024, 4, 10, 10, 0),
            end_time=datetime(2024, 4, 10, 10, 10),
            drone_id="primary"
        ),
        'others': [
            Mission(
                waypoints=[
                    Waypoint(x=0, y=100, timestamp=datetime(2024, 4, 10, 10, 0)),
                    Waypoint(x=100, y=100, timestamp=datetime(2024, 4, 10, 10, 5)),
                    Waypoint(x=200, y=100, timestamp=datetime(2024, 4, 10, 10, 10)),
                ],
                start_time=datetime(2024, 4, 10, 10, 0),
                end_time=datetime(2024, 4, 10, 10, 10),
                drone_id="traffic1"
            )
        ]
    }
    
    # Check mission safety using the query interface
    safety_check = check_mission_safety(missions['primary'], missions['others'])
    print("\nMission Safety Check Results (Conflict-Free Scenario):")
    print("=" * 50)
    print(safety_check["summary"])
    
    # Initialize plotter
    plotter = MissionPlotter()
    
    # Plot static visualization
    plotter.plot_all_missions(missions)
    plotter.save('conflict_free_visualization.png')
    
    # Create animation (faster with 500ms interval)
    plotter.plot_mission_animation(
        missions,
        interval=500,  # 0.5 seconds per frame
        save_path='conflict_free_animation.gif'
    )

def visualize_head_on_collision():
    """Visualize a head-on collision scenario."""
    # Create a head-on collision scenario
    missions = {
        'primary': Mission(
            waypoints=[
                Waypoint(x=0, y=100, timestamp=datetime(2024, 4, 10, 10, 0)),
                Waypoint(x=100, y=100, timestamp=datetime(2024, 4, 10, 10, 5)),
                Waypoint(x=200, y=100, timestamp=datetime(2024, 4, 10, 10, 10)),
            ],
            start_time=datetime(2024, 4, 10, 10, 0),
            end_time=datetime(2024, 4, 10, 10, 10),
            drone_id="primary"
        ),
        'others': [
            Mission(
                waypoints=[
                    Waypoint(x=200, y=100, timestamp=datetime(2024, 4, 10, 10, 0)),
                    Waypoint(x=100, y=100, timestamp=datetime(2024, 4, 10, 10, 5)),
                    Waypoint(x=0, y=100, timestamp=datetime(2024, 4, 10, 10, 10)),
                ],
                start_time=datetime(2024, 4, 10, 10, 0),
                end_time=datetime(2024, 4, 10, 10, 10),
                drone_id="traffic1"
            )
        ]
    }
    
    # Check mission safety using the query interface
    safety_check = check_mission_safety(missions['primary'], missions['others'])
    print("\nMission Safety Check Results (Head-on Collision Scenario):")
    print("=" * 50)
    print(safety_check["summary"])
    
    # Initialize plotter
    plotter = MissionPlotter()
    
    # Plot static visualization
    plotter.plot_all_missions(missions, safety_check["conflicts"])
    plotter.save('head_on_collision_visualization.png')
    
    # Create animation (faster with 500ms interval)
    plotter.plot_mission_animation(
        missions,
        safety_check["conflicts"],
        interval=500,  # 0.5 seconds per frame
        save_path='head_on_collision_animation.gif'
    )

def visualize_crossing_collision():
    """Visualize a scenario where drones cross paths at the center."""
    # Load collision scenarios from JSON
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_collision_scenarios.json')
    missions = DataLoader.load_from_json(json_path)
    
    # Check mission safety using the query interface
    safety_check = check_mission_safety(missions['primary'], missions['others'])
    print("\nMission Safety Check Results (Crossing Paths Scenario):")
    print("=" * 50)
    print(safety_check["summary"])
    
    # Initialize plotter
    plotter = MissionPlotter()
    
    # Plot static visualization
    plotter.plot_all_missions(missions, safety_check["conflicts"])
    plotter.save('crossing_collision_visualization.png')
    
    # Create animation (faster with 500ms interval)
    plotter.plot_mission_animation(
        missions,
        safety_check["conflicts"],
        interval=500,  # 0.5 seconds per frame
        save_path='crossing_collision_animation.gif'
    )

def visualize_head_on_collision_json():
    """Visualize a head-on collision scenario loaded from JSON."""
    # Load head-on collision scenario from JSON
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_head_on_collision.json')
    missions = DataLoader.load_from_json(json_path)
    
    # Check mission safety using the query interface
    safety_check = check_mission_safety(missions['primary'], missions['others'])
    print("\nMission Safety Check Results (Head-on Collision Scenario from JSON):")
    print("=" * 50)
    print(safety_check["summary"])
    
    # Initialize plotter
    plotter = MissionPlotter()
    
    # Plot static visualization
    plotter.plot_all_missions(missions, safety_check["conflicts"])
    plotter.save('head_on_collision_json_visualization.png')
    
    # Create animation (faster with 500ms interval)
    plotter.plot_mission_animation(
        missions,
        safety_check["conflicts"],
        interval=500,  # 0.5 seconds per frame
        save_path='head_on_collision_json_animation.gif'
    )

def visualize_4d_collision_scenario():
    """Visualize collision scenarios in 4D (3D space + time as color)."""
    # Load collision scenarios from JSON
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_collision_scenarios.json')
    missions = DataLoader.load_from_json(json_path)
    
    # Check mission safety using the query interface
    safety_check = check_mission_safety(missions['primary'], missions['others'])
    print("\nMission Safety Check Results (4D Visualization):")
    print("=" * 50)
    print(safety_check["summary"])
    
    # Initialize plotter
    plotter = MissionPlotter()
    
    # Plot 4D visualization
    plotter.plot_4d_all_missions(missions, safety_check["conflicts"])
    plotter.save_4d_visualization('4d_collision_visualization.png')
    
    print("\n4D Visualization saved as '4d_collision_visualization.png'")
    print("Color gradient represents time progression:")
    print("Blue -> Green -> Yellow -> Red")
    print("(Start) ------------------> (End)")

def visualize_3d_animation():
    """Visualize a 3D animation of drone missions with varied altitudes."""
    # Load 3D scenarios from JSON
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_3d_scenarios.json')
    missions = DataLoader.load_from_json(json_path)
    
    # Check mission safety using the query interface
    safety_check = check_mission_safety(missions['primary'], missions['others'])
    print("\nMission Safety Check Results (3D Animation):")
    print("=" * 50)
    print(safety_check["summary"])
    
    # Initialize plotter
    plotter = MissionPlotter()
    
    # Plot static visualization
    plotter.plot_all_missions(missions, safety_check["conflicts"])
    plotter.save('3d_static_visualization.png')
    
    # Create animation with slower speed (interval=500ms)
    plotter.plot_mission_animation(
        missions,
        safety_check["conflicts"],
        interval=500,  # Slower animation (500ms per frame)
        save_path='3d_animation.gif'
    )

def test_static_visualization():
    """Test static visualization of missions with conflicts."""
    print("Testing static visualization with conflicts...")
    
    # Load test scenarios
    missions = DataLoader.load_from_json('test_scenarios.json')
    
    # Check for conflicts
    detector = ConflictDetector(safety_buffer=50.0)  # 50m safety buffer
    status, conflicts = detector.check_mission(missions['primary'], missions['others'])
    
    print(f"Conflict check status: {status}")
    if conflicts:
        print(f"Found {len(conflicts)} conflicts:")
        for conflict in conflicts:
            print(f"- At {conflict.time}: {conflict.description}")
    
    # Create plotter
    plotter = MissionPlotter()
    
    # Plot all missions with conflicts
    plotter.plot_all_missions(missions, conflicts)
    
    # Save the plot
    plotter.save_plot('static_visualization.png')
    print("Static visualization saved as 'static_visualization.png'")

def test_animated_visualization():
    """Test animated visualization of missions with conflicts."""
    print("Testing animated visualization with conflicts...")
    
    # Load test scenarios
    missions = DataLoader.load_from_json('test_scenarios.json')
    
    # Check for conflicts
    detector = ConflictDetector(safety_buffer=50.0)  # 50m safety buffer
    status, conflicts = detector.check_mission(missions['primary'], missions['others'])
    
    print(f"Conflict check status: {status}")
    if conflicts:
        print(f"Found {len(conflicts)} conflicts:")
        for conflict in conflicts:
            print(f"- At {conflict.time}: {conflict.description}")
    
    # Create plotter
    plotter = MissionPlotter()
    
    # Create animation with conflicts
    plotter.create_animation(missions, conflicts, interval=100)  # 100ms between frames
    
    # Save the animation
    plotter.save_animation('animation.gif', fps=10)
    print("Animation saved as 'animation.gif'")

if __name__ == "__main__":
    print("Starting visualization tests...")
    
    # Test static visualization with conflicts
    test_static_visualization()
    
    # Test animated visualization with conflicts
    test_animated_visualization()
    
    print("Visualization tests completed.") 