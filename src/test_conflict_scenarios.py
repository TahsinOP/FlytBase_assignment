from data.data_loader import DataLoader
from visualization.plotter import MissionPlotter
import os

def test_conflict_scenarios():
    """Test visualization of conflict scenarios from JSON file."""
    print("\nTesting Conflict Scenarios Visualization...")
    
    # Load mission data from JSON file
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_scenarios.json')
    missions = DataLoader.load_from_json(json_path)
    
    # Create plotter and visualize
    plotter = MissionPlotter()
    
    # First plot static visualization
    plotter.plot_all_missions(missions)
    plotter.save('conflict_scenario_static.png')
    print("Static visualization saved as 'conflict_scenario_static.png'")
    
    # Then create animation
    plotter.plot_mission_animation(missions, save_path='conflict_scenario_animation.gif')
    print("Animation saved as 'conflict_scenario_animation.gif'")

if __name__ == "__main__":
    test_conflict_scenarios() 