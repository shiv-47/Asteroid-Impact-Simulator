import math
import json
import matplotlib.pyplot as plt
import numpy as np

class AsteroidTracker:
    def __init__(self):
        self.MOON_RADIUS = 1079
        self.ASTEROID_SPEED = 9000  # Increased speed to reach Moon in 28 days
        self.COLLISION_DAYS = 28
        self.TOTAL_HOURS = self.COLLISION_DAYS * 24
        self.EARTH_TO_MOON = 238900  # Earth to Moon distance in miles
        
        # Asteroid starts near Saturn
        self.saturn_x = 0
        self.saturn_y = 0
        self.saturn_z = 0
        
        # Moon is the target
        self.moon_x = self.EARTH_TO_MOON
        self.moon_y = 0
        self.moon_z = 0
        
        self.trajectory = []
        self.collision_detected = False
        self.collision_time = None
        
    def calculate_trajectory(self):
        for hour in range(0, self.TOTAL_HOURS + 1):
            distance_traveled = self.ASTEROID_SPEED * hour
            days = hour / 24
            progress = hour / self.TOTAL_HOURS  # 0 to 1
            
            # 3D trajectory with curved path that converges to moon
            x = distance_traveled
            amplitude = (1 - progress)  # Dampen oscillations as it approaches
            y = 3000 * amplitude * math.sin(progress * math.pi * 4)  # Curved motion in Y
            z = 2000 * amplitude * math.cos(progress * math.pi * 3)  # Curved motion in Z
            
            # Calculate distance to moon center
            dist_to_moon = math.sqrt((self.moon_x - x)**2 + y**2 + z**2)
            
            self.trajectory.append({
                'time_days': round(days, 2),
                'position': {'x': round(x, 2), 'y': round(y, 2), 'z': round(z, 2)},
                'distance_to_moon': round(dist_to_moon, 2)
            })
            
            if dist_to_moon < self.MOON_RADIUS and not self.collision_detected:
                self.collision_detected = True
                self.collision_time = days

    def plot_visuals(self):
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        x_vals = [p['position']['x'] for p in self.trajectory]
        y_vals = [p['position']['y'] for p in self.trajectory]
        z_vals = [p['position']['z'] for p in self.trajectory]
        
        ax.plot(x_vals, y_vals, z_vals, label='Asteroid Path', color='cyan', linewidth=2)
        ax.scatter(0, 0, 0, color='orange', s=150, label='Saturn (Start)')
        ax.scatter(self.moon_x, 0, 0, color='purple', s=200, label='Moon (Target)')
        
        if self.collision_detected:
            ax.scatter(self.moon_x, 0, 0, color='red', marker='X', s=300, label='IMPACT')

        ax.set_title(f"Asteroid Impact Simulation from Saturn: Day {self.COLLISION_DAYS}")
        ax.set_xlabel("Distance X (Miles)")
        ax.set_ylabel("Distance Y (Miles)")
        ax.set_zlabel("Distance Z (Miles)")
        ax.legend()
        print(f"IMPACT DETECTED AT DAY: {self.collision_time}")

tracker = AsteroidTracker()
tracker.calculate_trajectory()
tracker.plot_visuals()
plt.show()