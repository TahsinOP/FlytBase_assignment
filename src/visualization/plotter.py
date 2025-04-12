import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from models.mission import Mission, Waypoint
from conflict.conflict_detector import Conflict, ConflictDetector
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider

class MissionPlotter:
    """Handles 3D visualization of drone missions and conflicts."""
    
    def __init__(self):
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.stored_waypoints = None
        self.conflicts = None
        
        # Create a custom colormap for time visualization
        colors = ['blue', 'green', 'yellow', 'red']
        self.time_cmap = LinearSegmentedColormap.from_list('time_cmap', colors)
        
        # Add control buttons
        self.ax_play = plt.axes([0.7, 0.05, 0.1, 0.04])
        self.ax_reset = plt.axes([0.81, 0.05, 0.1, 0.04])
        self.ax_slider = plt.axes([0.1, 0.05, 0.5, 0.04])
        
        self.play_button = Button(self.ax_play, 'Play/Pause')
        self.reset_button = Button(self.ax_reset, 'Reset View')
        self.time_slider = Slider(self.ax_slider, 'Time', 0, 1, valinit=0)
        
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        
        self.colors = {
            'primary': 'red',
            'traffic1': 'blue',
            'traffic2': 'green',
            'traffic3': 'purple',
            'traffic4': 'orange'
        }
    
    def plot_mission(self, mission: Mission, color: str, show_trail: bool = True):
        """Plot a single mission's waypoints and path."""
        x = [wp.x for wp in mission.waypoints]
        y = [wp.y for wp in mission.waypoints]
        z = [wp.z for wp in mission.waypoints]
        times = [wp.timestamp.strftime('%H:%M:%S') for wp in mission.waypoints]
        
        # Plot path
        self.ax.plot(x, y, z, color=color, linewidth=2, label=f'{mission.drone_id} Path')
        
        # Plot waypoints
        scatter = self.ax.scatter(x, y, z, color=color, s=50, label=f'{mission.drone_id} Waypoints')
        
        # Add time labels
        for i, (xi, yi, zi, time) in enumerate(zip(x, y, z, times)):
            self.ax.text(xi, yi, zi, f'WP{i+1}\n{time}', color=color)
        
        if show_trail:
            # Add trailing effect
            for i in range(1, len(x)):
                self.ax.plot(x[:i+1], y[:i+1], z[:i+1], color=color, linestyle=':', alpha=0.5)
    
    def plot_conflicts(self, conflicts: List[Conflict]):
        """Plot conflict points and safety buffers."""
        self.conflicts = conflicts
        
        for conflict in conflicts:
            # Plot conflict point
            self.ax.scatter(
                conflict.location[0], 
                conflict.location[1], 
                0,
                color='black', 
                s=100, 
                marker='*',
                label=f'Conflict at {conflict.time.strftime("%H:%M:%S")}'
            )
            
            # Plot safety buffer circle
            theta = np.linspace(0, 2*np.pi, 100)
            x = conflict.location[0] + conflict.distance * np.cos(theta)
            y = conflict.location[1] + conflict.distance * np.sin(theta)
            z = np.zeros_like(x)
            
            self.ax.plot(x, y, z, 'r--', alpha=0.3, label='Safety Buffer')
    
    def plot_all_missions(self, missions: Dict[str, List[Mission]], conflicts: Optional[List[Conflict]] = None):
        """Plot all missions and conflicts if provided."""
        # Clear previous plot
        self.ax.clear()
        
        # Reset limits
        self.x_min = float('inf')
        self.x_max = float('-inf')
        self.y_min = float('inf')
        self.y_max = float('-inf')
        
        # Store the waypoints for animation
        self.stored_waypoints = {
            'primary': missions['primary'].waypoints,
            'others': {mission.drone_id: mission.waypoints for mission in missions['others']}
        }
        
        # Plot primary mission
        self.plot_mission(missions['primary'], self.colors['primary'])
        
        # Plot traffic drones
        for mission in missions['others']:
            color = self.colors.get(mission.drone_id, 'gray')
            self.plot_mission(mission, color)
        
        # Plot conflicts if provided
        if conflicts:
            self.plot_conflicts(conflicts)
        
        # Set labels and title
        self.ax.set_xlabel('X (meters)')
        self.ax.set_ylabel('Y (meters)')
        self.ax.set_zlabel('Z (meters)')
        self.ax.set_title('Drone Mission Visualization')
        
        # Add legend
        self.ax.legend()
        
        # Set equal aspect ratio
        self.ax.set_box_aspect([1, 1, 1])
        
        # Set initial view
        self.ax.view_init(elev=20, azim=45)
        
        # Add grid
        self.ax.grid(True)
    
    def create_animation(self, missions: Dict[str, List[Mission]], 
                        conflicts: Optional[List[Conflict]] = None,
                        interval: int = 100):
        """Create an animated visualization."""
        # Get all waypoints in order
        all_waypoints = []
        for wp in missions['primary'].waypoints:
            if wp.timestamp:
                all_waypoints.append(('primary', wp))
        
        for mission in missions['others']:
            for wp in mission.waypoints:
                if wp.timestamp:
                    all_waypoints.append((mission.drone_id, wp))
        
        all_waypoints.sort(key=lambda x: x[1].timestamp)
        self.total_frames = len(all_waypoints)
        
        def update(frame):
            self.current_frame = frame
            self.time_slider.set_val(frame / self.total_frames)
            
            # Clear previous plot
            self.ax.clear()
            
            # Group waypoints by mission up to current frame
            mission_waypoints = {}
            for mission_id, wp in all_waypoints[:frame+1]:
                if mission_id not in mission_waypoints:
                    mission_waypoints[mission_id] = []
                mission_waypoints[mission_id].append(wp)
            
            # Plot each mission's progress
            for mission_id, waypoints in mission_waypoints.items():
                x = [wp.x for wp in waypoints]
                y = [wp.y for wp in waypoints]
                z = [wp.z for wp in waypoints]
                times = [wp.timestamp.strftime('%H:%M:%S') for wp in waypoints]
                
                color = self.colors.get(mission_id, 'gray')
                
                # Plot path
                self.ax.plot(x, y, z, color=color, linewidth=2)
                
                # Plot current position
                self.ax.scatter(x[-1:], y[-1:], z[-1:], color=color, s=100)
                self.ax.text(x[-1], y[-1], z[-1], times[-1], color=color)
            
            # Plot conflicts if they've occurred
            if conflicts:
                current_time = all_waypoints[frame][1].timestamp
                for conflict in conflicts:
                    if conflict.time <= current_time:
                        self.plot_conflicts([conflict])
            
            # Update title with current time
            current_time = all_waypoints[frame][1].timestamp
            self.ax.set_title(f'Drone Mission Animation\nTime: {current_time.strftime("%H:%M:%S")}')
            
            # Rotate view for better 3D perspective
            self.ax.view_init(elev=20, azim=(frame % 360))
            
            return self.ax
        
        def play_pause(event):
            self.is_playing = not self.is_playing
            if self.is_playing:
                self.ani.event_source.start()
            else:
                self.ani.event_source.stop()
        
        def reset_view(event):
            self.ax.view_init(elev=20, azim=45)
            self.fig.canvas.draw_idle()
        
        def update_slider(val):
            frame = int(val * self.total_frames)
            if frame != self.current_frame:
                self.current_frame = frame
                update(frame)
                self.fig.canvas.draw_idle()
        
        # Create animation
        self.ani = animation.FuncAnimation(
            self.fig, update, frames=self.total_frames,
            interval=interval, blit=False
        )
        
        # Connect controls
        self.play_button.on_clicked(play_pause)
        self.reset_button.on_clicked(reset_view)
        self.time_slider.on_changed(update_slider)
        
        # Show the plot
        plt.tight_layout()
        plt.show()
    
    def save_animation(self, filename: str, fps: int = 10):
        """Save the animation to a file."""
        if self.ani:
            self.ani.save(filename, writer='pillow', fps=fps)
    
    def save_plot(self, filename: str):
        """Save the current plot to a file."""
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    
    def _update_plot_limits(self, x: List[float], y: List[float]):
        """Update plot limits based on coordinates."""
        if not hasattr(self, 'x_min'):
            self.x_min = min(x)
            self.x_max = max(x)
            self.y_min = min(y)
            self.y_max = max(y)
        else:
            self.x_min = min(self.x_min, min(x))
            self.x_max = max(self.x_max, max(x))
            self.y_min = min(self.y_min, min(y))
            self.y_max = max(self.y_max, max(y))
        
        # Add padding
        padding = 50
        self.ax.set_xlim(self.x_min - padding, self.x_max + padding)
        self.ax.set_ylim(self.y_min - padding, self.y_max + padding)
    
    def show(self):
        """Display the plot."""
        plt.tight_layout()
        plt.show()
    
    def save(self, filename: str):
        """Save the plot to a file."""
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_4d_mission(self, mission: Mission, start_time: datetime, end_time: datetime, 
                       color: str = 'blue', label: str = None):
        """Plot a mission in 4D (3D space + time as color)."""
        # Extract coordinates and timestamps
        x = [wp.x for wp in mission.waypoints]
        y = [wp.y for wp in mission.waypoints]
        z = [wp.z for wp in mission.waypoints]
        times = [wp.timestamp for wp in mission.waypoints]
        
        # Normalize timestamps to [0,1] for color mapping
        time_norm = [(t - start_time).total_seconds() / 
                    (end_time - start_time).total_seconds() 
                    for t in times]
        
        # Plot waypoints with time-based colors
        scatter = self.ax.scatter(x, y, z, c=time_norm, cmap=self.time_cmap, 
                                s=100, label=label or mission.drone_id)
        
        # Plot path with time-based colors
        for i in range(len(x)-1):
            self.ax.plot(x[i:i+2], y[i:i+2], z[i:i+2], 
                        color=self.time_cmap(time_norm[i]), 
                        linestyle='-', linewidth=2)
        
        # Add waypoint labels with time information
        for i, (xi, yi, zi, ti) in enumerate(zip(x, y, z, times)):
            time_str = ti.strftime('%H:%M:%S')
            self.ax.text(xi, yi, zi, f'WP{i+1}\n{time_str}', 
                        color=self.time_cmap(time_norm[i]))
        
        return scatter
    
    def plot_4d_conflicts(self, conflicts: List[Conflict], start_time: datetime, 
                         end_time: datetime):
        """Plot conflicts in 4D (3D space + time as color)."""
        self.conflicts = conflicts
        
        for conflict in conflicts:
            # Normalize conflict time for color mapping
            time_norm = (conflict.time - start_time).total_seconds() / \
                       (end_time - start_time).total_seconds()
            
            # Plot conflict point with time-based color
            self.ax.scatter(
                conflict.location[0], 
                conflict.location[1], 
                0,  # Set z-coordinate to 0 for 2D conflicts
                color=self.time_cmap(time_norm),
                s=200, 
                marker='*',
                label=f'Conflict at {conflict.time.strftime("%H:%M:%S")}'
            )
            
            # Plot safety buffer circle (2D)
            theta = np.linspace(0, 2 * np.pi, 100)
            x = conflict.location[0] + conflict.distance * np.cos(theta)
            y = conflict.location[1] + conflict.distance * np.sin(theta)
            z = np.zeros_like(x)  # All points at z=0
            
            self.ax.plot(x, y, z, color=self.time_cmap(time_norm), 
                        alpha=0.2, label='Safety Buffer')
            
            # Add conflict label with time
            self.ax.text(
                conflict.location[0], 
                conflict.location[1], 
                0,  # Set z-coordinate to 0 for 2D conflicts
                f'Conflict\n{conflict.time.strftime("%H:%M:%S")}\n{conflict.conflicting_drone}',
                color=self.time_cmap(time_norm)
            )
    
    def plot_4d_all_missions(self, missions: Dict[str, List[Mission]], 
                           conflicts: Optional[List[Conflict]] = None):
        """Plot all missions and conflicts in 4D (3D space + time as color)."""
        # Clear previous plot
        self.ax.clear()
        
        # Get time range for color normalization
        start_time = min(
            missions['primary'].start_time,
            min(m.start_time for m in missions['others'])
        )
        end_time = max(
            missions['primary'].end_time,
            max(m.end_time for m in missions['others'])
        )
        
        # Plot primary mission
        scatter1 = self.plot_4d_mission(
            missions['primary'], 
            start_time, 
            end_time,
            color='red', 
            label='Primary Drone'
        )
        
        # Plot traffic drones
        colors = ['blue', 'green', 'purple', 'orange', 'cyan', 'magenta']
        scatters = []
        for i, mission in enumerate(missions['others']):
            scatter = self.plot_4d_mission(
                mission, 
                start_time, 
                end_time,
                color=colors[i % len(colors)]
            )
            scatters.append(scatter)
        
        # Plot conflicts if provided
        if conflicts:
            self.plot_4d_conflicts(conflicts, start_time, end_time)
        
        # Set labels and title
        self.ax.set_xlabel('X (meters)')
        self.ax.set_ylabel('Y (meters)')
        self.ax.set_zlabel('Z (meters)')
        self.ax.set_title('4D Drone Mission Visualization (Time as Color)')
        
        # Add colorbar for time
        norm = mcolors.Normalize(vmin=0, vmax=1)
        sm = plt.cm.ScalarMappable(cmap=self.time_cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=self.ax)
        cbar.set_label('Time Progression')
        
        # Add legend
        self.ax.legend()
        
        # Add grid
        self.ax.grid(True)
        
        # Set equal aspect ratio
        self.ax.set_box_aspect([1, 1, 1])
        
        # Force a redraw
        plt.draw()
    
    def save_4d_visualization(self, filename: str):
        """Save the 4D visualization to a file."""
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close() 