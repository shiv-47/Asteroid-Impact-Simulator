import math
import csv
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class AsteroidTracker:
    def __init__(self):
        self.MOON_RADIUS = 1737000  # meters (moon radius)
        self.G = 6.67430e-11  # Gravitational constant
        self.MOON_MASS = 7.342e22  # Moon mass in kg
        self.ASTEROID_TYPE = "C-type Carbonaceous"
        self.ASTEROID_DENSITY = 1300  # kg/m³
        self.ASTEROID_DIAMETER = 1000  # meters, approximate asteroid size
        self.ASTEROID_IMPACT_SPEED = 20000  # m/s, typical impact velocity in space
        self.COLLISION_DAYS = 5  # Set to 5 days for faster test
        self.TOTAL_HOURS = self.COLLISION_DAYS * 24
        self.EARTH_TO_MOON = 384400000  # Earth to Moon distance in meters
        self.ASTEROID_SPEED = self.EARTH_TO_MOON / (self.TOTAL_HOURS * 3600)  # meters per second to reach in time
        
        # Asteroid starts near Saturn
        self.saturn_x = 0
        self.saturn_y = 0
        self.saturn_z = 0
        
        # Moon is the target
        self.moon_x = self.EARTH_TO_MOON
        self.moon_y = 0
        self.moon_z = 0
        
        # Initial asteroid position and velocity
        self.asteroid_x = 0.0  # Start from Saturn/Earth
        self.asteroid_y = 0.0
        self.asteroid_z = 0.0
        self.asteroid_vx = self.ASTEROID_SPEED  # Towards Moon
        self.asteroid_vy = 0.0  # Straight
        self.asteroid_vz = 0.0
        
        self.trajectory = []
        self.collision_detected = False
        self.collision_time = None
        self.impact_depth_m = 0.0
        self.moonquake_magnitude = None
        self.impact_velocity = 0.0
        
    def calculate_kinetic_energy(self, mass_kg, speed_m_s):
        """Return kinetic energy KE = 1/2 * m * v^2 in Joules."""
        # KE = 1/2 * m * v^2, where m is mass in kg and v is speed in m/s
        return 0.5 * mass_kg * speed_m_s**2

    def calculate_moonquake_magnitude(self, energy_joules):
        """Estimate a moonquake magnitude from impact energy in Joules.

        Uses an approximate seismic scaling relation:
        log10(E) = 1.5 * M + 4.8, where E is energy in joules and M is magnitude.
        """
        if energy_joules <= 0:
            return 0.0
        return round((math.log10(energy_joules) - 4.8) / 1.5, 2)

    def estimate_impact_depth(self):
        radius_m = self.ASTEROID_DIAMETER / 2.0
        volume_m3 = 4.0 / 3.0 * math.pi * radius_m**3
        mass_kg = self.ASTEROID_DENSITY * volume_m3
        kinetic_energy = self.calculate_kinetic_energy(mass_kg, self.impact_velocity)
        depth_m = max(1.0, 2.0 * (kinetic_energy / 1e15) ** 0.25)
        return round(depth_m, 2), mass_kg, kinetic_energy

    def calculate_trajectory(self):
        dt = 3600.0  # Time step in seconds (1 hour)
        for hour in range(0, self.TOTAL_HOURS + 1):
            days = hour / 24
            
            # Calculate distance to moon
            dx = self.moon_x - self.asteroid_x
            dy = self.moon_y - self.asteroid_y
            dz = self.moon_z - self.asteroid_z
            r = math.sqrt(dx**2 + dy**2 + dz**2)
            
            # Adaptive time step to prevent overshoot
            if r < 2 * self.MOON_RADIUS:
                dt = 60.0  # 1 minute when close
            else:
                dt = 3600.0  # 1 hour otherwise
            
            # Gravitational acceleration towards moon
            if r > 0:
                a = self.G * self.MOON_MASS / r**2
                ax = a * dx / r
                ay = a * dy / r
                az = a * dz / r
            else:
                ax = ay = az = 0
            
            # Update velocity
            self.asteroid_vx += ax * dt
            self.asteroid_vy += ay * dt
            self.asteroid_vz += az * dt
            
            # Update position
            self.asteroid_x += self.asteroid_vx * dt
            self.asteroid_y += self.asteroid_vy * dt
            self.asteroid_z += self.asteroid_vz * dt
            
            # Recalculate distance after update
            dist_to_moon = math.sqrt((self.moon_x - self.asteroid_x)**2 + self.asteroid_y**2 + self.asteroid_z**2)
            
            if dist_to_moon < self.MOON_RADIUS and not self.collision_detected:
                self.collision_detected = True
                self.collision_time = days
                self.impact_velocity = math.sqrt(self.asteroid_vx**2 + self.asteroid_vy**2 + self.asteroid_vz**2)
                self.impact_depth_m, mass_kg, kinetic_energy = self.estimate_impact_depth()
                self.moonquake_magnitude = self.calculate_moonquake_magnitude(kinetic_energy)
                print(f"COLLISION! Distance: {dist_to_moon:.2f}, Day: {days}, Position: ({self.asteroid_x:.2f}, {self.asteroid_y:.2f}, {self.asteroid_z:.2f}), Impact Depth: {self.impact_depth_m:.2f} m")
                print(f"Energy: {kinetic_energy:.2e} Joules")
                print(f"KE formula: 0.5 * m * v^2 = 0.5 * {mass_kg:.2e} kg * ({self.impact_velocity:.0f} m/s)^2")
                print(f"Estimated moonquake magnitude: {self.moonquake_magnitude:.2f}")

            impact_depth = self.impact_depth_m if self.collision_detected else 0.0
            self.trajectory.append({
                'time_days': round(days, 2),
                'position': {'x': round(self.asteroid_x, 2), 'y': round(self.asteroid_y, 2), 'z': round(self.asteroid_z, 2)},
                'distance_to_moon': round(dist_to_moon, 2),
                'impact_depth_m': round(impact_depth, 2),
                'moonquake_magnitude': self.moonquake_magnitude
            })
            
            # Debug: Print when getting close
            if dist_to_moon < 10000 and hour % 24 == 0:
                print(f"Day {days}: Distance to moon = {dist_to_moon:.2f} meters, Position: ({self.asteroid_x:.2f}, {self.asteroid_y:.2f}, {self.asteroid_z:.2f})")

    def _build_plot_fig(self):
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(211, projection='3d')
        ax2 = fig.add_subplot(212)

        x_vals = [p['position']['x'] for p in self.trajectory]
        y_vals = [p['position']['y'] for p in self.trajectory]
        z_vals = [p['position']['z'] for p in self.trajectory]
        days = [p['time_days'] for p in self.trajectory]
        depth_vals = [p['impact_depth_m'] for p in self.trajectory]
        dist_vals = [p['distance_to_moon'] for p in self.trajectory]

        ax.plot(x_vals, y_vals, z_vals, label='Asteroid Path', color='cyan', linewidth=2)
        ax.scatter(0, 0, 0, color='orange', s=150, label='Saturn (Start)')
        ax.scatter(self.moon_x, 0, 0, color='purple', s=200, label='Moon (Target)')

        if self.collision_detected:
            ax.scatter(self.moon_x, 0, 0, color='red', marker='X', s=300, label='IMPACT')

        ax.set_title(f"{self.ASTEROID_TYPE} Impact Simulation from Saturn")
        ax.set_xlabel("Distance X (Meters)")
        ax.set_ylabel("Distance Y (Meters)")
        ax.set_zlabel("Distance Z (Meters)")
        ax.legend()

        ax2.plot(days, depth_vals, label='Estimated Impact Depth', color='magenta', linewidth=2)
        if self.collision_detected:
            ax2.axvline(self.collision_time, color='red', linestyle='--', label=f'Impact at Day {self.collision_time}')
            ax2.text(self.collision_time, max(depth_vals) * 0.8 if depth_vals else 1, f'{self.impact_depth_m:.2f} m', color='red')
            if self.moonquake_magnitude is not None:
                ax2.text(0.05, 0.85, f'Moonquake magnitude (est.): {self.moonquake_magnitude:.2f}', transform=ax2.transAxes, color='blue')

        ax2.set_title('Estimated Impact Depth Over Time')
        ax2.set_xlabel('Time (Days)')
        ax2.set_ylabel('Impact Depth (m)')
        ax2.set_ylim(0, 10)
        ax2.grid(True)
        ax2.legend()

        return fig

    def plot_visuals(self):
        fig = self._build_plot_fig()
        print(f"IMPACT DETECTED AT DAY: {self.collision_time}")
        plt.show()

    def save_graph(self, filename='asteroid_impact_graph.png'):
        fig = self._build_plot_fig()
        fig.savefig(filename, dpi=200)
        plt.close(fig)
        print(f"Graph saved: {filename}")
    
    def create_video(self, filename='asteroid_trajectory.mp4', fps=30):
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Set up the plot limits
        x_vals = [p['position']['x'] for p in self.trajectory]
        y_vals = [p['position']['y'] for p in self.trajectory]
        z_vals = [p['position']['z'] for p in self.trajectory]
        
        ax.set_xlim(min(x_vals) - 10000, max(x_vals) + 10000)
        ax.set_ylim(min(y_vals) - 5000, max(y_vals) + 5000)
        ax.set_zlim(min(z_vals) - 5000, max(z_vals) + 5000)
        
        # Plot static elements
        ax.scatter(0, 0, 0, color='orange', s=150, label='Saturn (Start)')
        ax.scatter(self.moon_x, 0, 0, color='purple', s=200, label='Moon (Target)')
        
        # Plot the full trajectory path
        ax.plot(x_vals, y_vals, z_vals, label='Asteroid Path', color='cyan', linewidth=1, alpha=0.3)
        
        ax.set_title(f"Asteroid Impact Simulation from Saturn")
        ax.set_xlabel("Distance X (Meters)")
        ax.set_ylabel("Distance Y (Meters)")
        ax.set_zlabel("Distance Z (Meters)")
        ax.legend()
        
        # Animation elements
        line, = ax.plot([], [], [], 'r-', linewidth=2, label='Trail')
        point, = ax.plot([], [], [], 'ro', markersize=8)
        time_text = ax.text2D(0.05, 0.95, '', transform=ax.transAxes)
        magnitude_text = ax.text2D(0.05, 0.90, '', transform=ax.transAxes)
        
        def init():
            line.set_data([], [])
            line.set_3d_properties([])
            point.set_data([], [])
            point.set_3d_properties([])
            time_text.set_text('')
            magnitude_text.set_text('')
            return line, point, time_text, magnitude_text
        
        def animate(frame):
            # Show trail and current position
            trail_length = min(frame + 1, len(self.trajectory))
            trail = self.trajectory[:trail_length]
            
            x_trail = [p['position']['x'] for p in trail]
            y_trail = [p['position']['y'] for p in trail]
            z_trail = [p['position']['z'] for p in trail]
            
            line.set_data(x_trail, y_trail)
            line.set_3d_properties(z_trail)
            
            # Current position
            if trail:
                x_pos = trail[-1]['position']['x']
                y_pos = trail[-1]['position']['y']
                z_pos = trail[-1]['position']['z']
                point.set_data([x_pos], [y_pos])
                point.set_3d_properties([z_pos])
                
                day = trail[-1]['time_days']
                distance = trail[-1]['distance_to_moon']
                time_text.set_text(f'Day: {day:.1f} | Distance to Moon: {distance:.0f} m')
                if self.collision_detected and day >= self.collision_time:
                    magnitude_text.set_text(f'Estimated moonquake magnitude: {self.moonquake_magnitude:.2f}')
                else:
                    magnitude_text.set_text('')
            
            return line, point, time_text, magnitude_text
        
        # Create animation
        anim = animation.FuncAnimation(
            fig, animate, init_func=init,
            frames=len(self.trajectory),
            interval=1000/fps,  # Convert fps to milliseconds
            blit=False, repeat=True
        )
        
        # Save animation
        print(f"Creating video: {filename}...")
        try:
            anim.save(filename, writer='ffmpeg', fps=fps)
            print(f"Video saved: {filename}")
        except Exception as e:
            print(f"Error saving video: {e}")
            print("FFmpeg not installed. Saving as GIF instead...")
            try:
                anim.save(filename.replace('.mp4', '.gif'), writer='pillow', fps=fps)
                print(f"GIF saved: {filename.replace('.mp4', '.gif')}")
            except Exception as e2:
                print(f"Error saving GIF: {e2}")
            fig.savefig(filename.replace('.mp4', '.png'), dpi=200)
            print(f"Static image saved: {filename.replace('.mp4', '.png')}")

tracker = AsteroidTracker()
tracker.calculate_trajectory()
tracker.create_video('asteroid_trajectory.mp4', fps=30)
tracker.save_graph('asteroid_impact_graph.png')
tracker.plot_visuals()