from data.data_loader import DataLoader
from conflict.conflict_detector import ConflictDetector
import json
import os

def test_conflict_detection():
    """Test the conflict detection system with sample data."""
    # Load test scenarios
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_scenarios.json')
    missions = DataLoader.load_from_json(json_path)
    
    # Initialize conflict detector with 50m safety buffer
    detector = ConflictDetector(safety_buffer=50.0)
    
    # Check for conflicts
    status, conflicts = detector.check_mission(missions['primary'], missions['others'])
    
    # Print results
    print(f"\nMission Status: {status}")
    if conflicts:
        print("\nDetected Conflicts:")
        for i, conflict in enumerate(conflicts, 1):
            print(f"\nConflict {i}:")
            print(f"Location: ({conflict.location[0]:.2f}, {conflict.location[1]:.2f})")
            print(f"Time: {conflict.time.strftime('%H:%M:%S')}")
            print(f"Primary Drone: {conflict.primary_drone}")
            print(f"Conflicting Drone: {conflict.conflicting_drone}")
            print(f"Distance: {conflict.distance:.2f}m")
            print(f"Description: {conflict.description}")
    else:
        print("\nNo conflicts detected.")

def test_with_different_buffer():
    """Test conflict detection with different safety buffer sizes."""
    # Load test scenarios
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_scenarios.json')
    missions = DataLoader.load_from_json(json_path)
    
    # Test different buffer sizes
    buffer_sizes = [30.0, 50.0, 100.0]
    
    for buffer in buffer_sizes:
        print(f"\nTesting with safety buffer: {buffer}m")
        detector = ConflictDetector(safety_buffer=buffer)
        status, conflicts = detector.check_mission(missions['primary'], missions['others'])
        
        print(f"Status: {status}")
        print(f"Number of conflicts detected: {len(conflicts)}")
        if conflicts:
            print("First conflict details:")
            print(f"Location: ({conflicts[0].location[0]:.2f}, {conflicts[0].location[1]:.2f})")
            print(f"Time: {conflicts[0].time.strftime('%H:%M:%S')}")
            print(f"Distance: {conflicts[0].distance:.2f}m")

if __name__ == "__main__":
    print("Testing Conflict Detection System")
    print("=" * 50)
    
    print("\nTest 1: Basic Conflict Detection")
    test_conflict_detection()
    
    print("\nTest 2: Different Safety Buffer Sizes")
    test_with_different_buffer() 