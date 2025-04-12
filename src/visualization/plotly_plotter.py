import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Optional
from models.mission import Mission
from conflict.conflict_detector import Conflict
from datetime import datetime

class PlotlyMissionPlotter:
    """Handles 3D visualization of drone missions using Plotly."""
    
    def __init__(self):
        self.fig = go.Figure()
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
        
        # Plot path with hover information
        self.fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(color=color, width=4),
            name=f'{mission.drone_id} Path',
            showlegend=True,
            hovertemplate='<b>%{text}</b><br>' +
                        'X: %{x:.1f}<br>' +
                        'Y: %{y:.1f}<br>' +
                        'Z: %{z:.1f}<extra></extra>',
            text=times
        ))
        
        # Plot waypoints with hover information
        self.fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers+text',
            marker=dict(
                size=8,
                color=color,
                symbol='circle'
            ),
            text=times,
            textposition="top center",
            name=f'{mission.drone_id} Waypoints',
            showlegend=True,
            hovertemplate='<b>%{text}</b><br>' +
                        'X: %{x:.1f}<br>' +
                        'Y: %{y:.1f}<br>' +
                        'Z: %{z:.1f}<extra></extra>'
        ))
        
        if show_trail:
            # Add trailing effect with hover information
            for i in range(1, len(x)):
                self.fig.add_trace(go.Scatter3d(
                    x=x[:i+1], y=y[:i+1], z=z[:i+1],
                    mode='lines',
                    line=dict(color=color, width=2, dash='dot'),
                    name=f'{mission.drone_id} Trail',
                    showlegend=False,
                    hovertemplate='<b>%{text}</b><br>' +
                                'X: %{x:.1f}<br>' +
                                'Y: %{y:.1f}<br>' +
                                'Z: %{z:.1f}<extra></extra>',
                    text=times[:i+1]
                ))
    
    def plot_conflict(self, conflict: Conflict):
        """Plot a conflict point and its safety buffer."""
        x = conflict.location[0]
        y = conflict.location[1]
        z = conflict.location[2] if len(conflict.location) > 2 else 0
        
        # Plot conflict point with hover information
        self.fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode='markers',
            marker=dict(
                size=15,
                color='black',
                symbol='diamond'
            ),
            name=f'Conflict at {conflict.time.strftime("%H:%M:%S")}',
            showlegend=True,
            hovertemplate='<b>Conflict</b><br>' +
                        'Time: %{text}<br>' +
                        'X: %{x:.1f}<br>' +
                        'Y: %{y:.1f}<br>' +
                        'Z: %{z:.1f}<br>' +
                        'Distance: %.1f m<extra></extra>' % conflict.distance,
            text=[conflict.time.strftime('%H:%M:%S')]
        ))
        
        # Create safety buffer sphere
        theta = np.linspace(0, 2*np.pi, 100)
        phi = np.linspace(0, np.pi, 100)
        x_sphere = x + conflict.distance * np.outer(np.cos(theta), np.sin(phi))
        y_sphere = y + conflict.distance * np.outer(np.sin(theta), np.sin(phi))
        z_sphere = z + conflict.distance * np.outer(np.ones(np.size(theta)), np.cos(phi))
        
        self.fig.add_trace(go.Surface(
            x=x_sphere, y=y_sphere, z=z_sphere,
            colorscale=[[0, 'rgba(255,0,0,0.1)'], [1, 'rgba(255,0,0,0.1)']],
            showscale=False,
            name='Safety Buffer',
            showlegend=True,
            hovertemplate='<b>Safety Buffer</b><br>' +
                        'Radius: %.1f m<extra></extra>' % conflict.distance
        ))
    
    def plot_all_missions(self, missions: Dict[str, List[Mission]], 
                         conflicts: Optional[List[Conflict]] = None):
        """Plot all missions and conflicts."""
        # Clear previous plot
        self.fig = go.Figure()
        
        # Plot primary mission
        self.plot_mission(missions['primary'], self.colors['primary'])
        
        # Plot traffic drones
        for mission in missions['others']:
            color = self.colors.get(mission.drone_id, 'gray')
            self.plot_mission(mission, color)
        
        # Plot conflicts if provided
        if conflicts:
            for conflict in conflicts:
                self.plot_conflict(conflict)
        
        # Update layout with enhanced controls
        self.fig.update_layout(
            title='Drone Mission Visualization',
            scene=dict(
                xaxis_title='X (meters)',
                yaxis_title='Y (meters)',
                zaxis_title='Z (meters)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[None, dict(frame=dict(duration=1000, redraw=True), 
                                            fromcurrent=True)]
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[[None], dict(frame=dict(duration=0, redraw=False), 
                                             mode="immediate")]
                        )
                    ],
                    direction="left",
                    pad=dict(r=10, t=10),
                    showactive=False,
                    x=0.1,
                    y=0,
                    xanchor="right",
                    yanchor="top"
                ),
                dict(
                    type="buttons",
                    buttons=[
                        dict(
                            label="Reset View",
                            method="relayout",
                            args=["scene.camera", dict(
                                eye=dict(x=1.5, y=1.5, z=1.5)
                            )]
                        )
                    ],
                    direction="left",
                    pad=dict(r=10, t=10),
                    showactive=False,
                    x=0.1,
                    y=0.1,
                    xanchor="right",
                    yanchor="top"
                )
            ]
        )
    
    def show(self):
        """Display the plot."""
        self.fig.show()
    
    def save(self, filename: str):
        """Save the plot to an HTML file."""
        self.fig.write_html(filename)
    
    def create_animation(self, missions: Dict[str, List[Mission]], 
                        conflicts: Optional[List[Conflict]] = None,
                        filename: str = 'animation.html'):
        """Create an animated visualization."""
        # Clear previous plot
        self.fig = go.Figure()
        
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
        
        # Create frames for animation
        frames = []
        for i in range(len(all_waypoints)):
            frame_data = []
            
            # Group waypoints by mission up to current frame
            mission_waypoints = {}
            for mission_id, wp in all_waypoints[:i+1]:
                if mission_id not in mission_waypoints:
                    mission_waypoints[mission_id] = []
                mission_waypoints[mission_id].append(wp)
            
            # Add traces for each mission
            for mission_id, waypoints in mission_waypoints.items():
                x = [wp.x for wp in waypoints]
                y = [wp.y for wp in waypoints]
                z = [wp.z for wp in waypoints]
                times = [wp.timestamp.strftime('%H:%M:%S') for wp in waypoints]
                
                color = self.colors.get(mission_id, 'gray')
                
                # Add path with hover information
                frame_data.append(go.Scatter3d(
                    x=x, y=y, z=z,
                    mode='lines',
                    line=dict(color=color, width=4),
                    name=f'{mission_id} Path',
                    hovertemplate='<b>%{text}</b><br>' +
                                'X: %{x:.1f}<br>' +
                                'Y: %{y:.1f}<br>' +
                                'Z: %{z:.1f}<extra></extra>',
                    text=times
                ))
                
                # Add current position with hover information
                frame_data.append(go.Scatter3d(
                    x=x[-1:], y=y[-1:], z=z[-1:],
                    mode='markers+text',
                    marker=dict(size=8, color=color, symbol='circle'),
                    text=[times[-1]],
                    textposition="top center",
                    name=f'{mission_id} Position',
                    hovertemplate='<b>%{text}</b><br>' +
                                'X: %{x:.1f}<br>' +
                                'Y: %{y:.1f}<br>' +
                                'Z: %{z:.1f}<extra></extra>'
                ))
            
            # Add conflict points if they've occurred
            if conflicts:
                current_time = all_waypoints[i][1].timestamp
                for conflict in conflicts:
                    if conflict.time <= current_time:
                        x = conflict.location[0]
                        y = conflict.location[1]
                        z = conflict.location[2] if len(conflict.location) > 2 else 0
                        
                        frame_data.append(go.Scatter3d(
                            x=[x], y=[y], z=[z],
                            mode='markers',
                            marker=dict(size=15, color='black', symbol='diamond'),
                            name=f'Conflict at {conflict.time.strftime("%H:%M:%S")}',
                            hovertemplate='<b>Conflict</b><br>' +
                                        'Time: %{text}<br>' +
                                        'X: %{x:.1f}<br>' +
                                        'Y: %{y:.1f}<br>' +
                                        'Z: %{z:.1f}<br>' +
                                        'Distance: %.1f m<extra></extra>' % conflict.distance,
                            text=[conflict.time.strftime('%H:%M:%S')]
                        ))
            
            frames.append(go.Frame(data=frame_data, name=f'frame_{i}'))
        
        # Add frames to figure
        self.fig.frames = frames
        
        # Set initial data
        self.fig.add_traces(frames[0].data)
        
        # Update layout with enhanced controls
        self.fig.update_layout(
            title='Drone Mission Animation',
            scene=dict(
                xaxis_title='X (meters)',
                yaxis_title='Y (meters)',
                zaxis_title='Z (meters)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[None, dict(frame=dict(duration=1000, redraw=True), 
                                            fromcurrent=True)]
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[[None], dict(frame=dict(duration=0, redraw=False), 
                                             mode="immediate")]
                        )
                    ],
                    direction="left",
                    pad=dict(r=10, t=10),
                    showactive=False,
                    x=0.1,
                    y=0,
                    xanchor="right",
                    yanchor="top"
                ),
                dict(
                    type="buttons",
                    buttons=[
                        dict(
                            label="Reset View",
                            method="relayout",
                            args=["scene.camera", dict(
                                eye=dict(x=1.5, y=1.5, z=1.5)
                            )]
                        )
                    ],
                    direction="left",
                    pad=dict(r=10, t=10),
                    showactive=False,
                    x=0.1,
                    y=0.1,
                    xanchor="right",
                    yanchor="top"
                )
            ],
            sliders=[dict(
                steps=[dict(
                    method='animate',
                    args=[[f'frame_{i}'], dict(mode='immediate', frame=dict(duration=0, redraw=True))],
                    label=f'Frame {i}'
                ) for i in range(len(frames))],
                active=0,
                transition=dict(duration=0),
                x=0.1,
                y=0,
                currentvalue=dict(
                    visible=True,
                    prefix='Time: ',
                    xanchor='right'
                ),
                len=0.9
            )]
        )
        
        # Save animation
        self.fig.write_html(filename) 