import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from packaging import version
from sscws.sscws import SscWs
import datetime
import csv
import numpy as np
from matplotlib.animation import FuncAnimation

# Create an instance of SscWs to access the SSCWS API (for ISS data)
ssc = SscWs()

# Global variables for view mode and satellite data (only ISS)
view_mode = "satellite"  # Options: "satellite" (close-up) or "system" (wide)
latest_coords_iss = None

# Create a Matplotlib figure with 3D axes
fig = plt.figure()
if version.parse(matplotlib.__version__) < version.parse('3.4'):
    ax = fig.gca(projection='3d')
else:
    ax = Axes3D(fig, auto_add_to_figure=False)
    fig.add_axes(ax)

ax.set_xlabel('X (km)')
ax.set_ylabel('Y (km)')
ax.set_zlabel('Z (km)')

# Create line plot and marker for ISS orbit
line_plot_iss, = ax.plot([], [], [], label='ISS Orbit', lw=2, color='red')
current_point_iss, = ax.plot([], [], [], 'ro', label='ISS', markersize=8)

ax.legend()

# Helper function to set equal aspect ratio in 3D so spheres render correctly
def set_axes_equal(ax):
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()
    x_range = abs(x_limits[1] - x_limits[0])
    y_range = abs(y_limits[1] - y_limits[0])
    z_range = abs(z_limits[1] - z_limits[0])
    plot_radius = 0.5 * max([x_range, y_range, z_range])
    x_middle = np.mean(x_limits)
    y_middle = np.mean(y_limits)
    z_middle = np.mean(z_limits)
    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

# Functions to draw Earth and Moon with improved resolution
def draw_earth(ax):
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    earth_radius = 6371  # km
    x = earth_radius * np.outer(np.cos(u), np.sin(v))
    y = earth_radius * np.outer(np.sin(u), np.sin(v))
    z = earth_radius * np.outer(np.ones(np.size(u)), np.cos(v))
    earth = ax.plot_surface(x, y, z, rstride=4, cstride=4, color='blue', alpha=0.3)
    return earth

def draw_moon(ax):
    # Assume the Moon is at a fixed approximate position for illustration purposes
    moon_center = (384400, 0, 0)  # km
    moon_radius = 1737           # km
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = moon_radius * np.outer(np.cos(u), np.sin(v)) + moon_center[0]
    y = moon_radius * np.outer(np.sin(u), np.sin(v)) + moon_center[1]
    z = moon_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + moon_center[2]
    moon = ax.plot_surface(x, y, z, rstride=4, cstride=4, color='gray', alpha=0.5)
    return moon

earth_artist = draw_earth(ax)
moon_artist = draw_moon(ax)

# Function to fetch ISS data using SSCWS API
def fetch_satellite_data(satellite_id, start_iso, end_iso):
    try:
        result = ssc.get_locations([satellite_id], [start_iso, end_iso])
        if len(result['Data']) == 0:
            print(f"No data returned for {satellite_id}.")
            return None
        data = result['Data'][0]
        if len(data['Coordinates']) == 0:
            print(f"No coordinate data for {satellite_id}.")
            return None
        coords = data['Coordinates'][0]
        return coords
    except Exception as e:
        print(f"Error fetching data for {satellite_id}:", e)
        return None

def update(frame):
    global latest_coords_iss, view_mode
    # Define a 1-hour time interval for ISS data
    start_time = datetime.datetime.utcnow()
    end_time = start_time + datetime.timedelta(hours=1)
    start_iso = start_time.isoformat() + "Z"
    end_iso = end_time.isoformat() + "Z"
    
    # Fetch ISS data using SSCWS API
    iss_coords = fetch_satellite_data('iss', start_iso, end_iso)
    if iss_coords is None:
        print("No ISS data available.")
        return line_plot_iss, current_point_iss
    latest_coords_iss = iss_coords
    X_iss = np.array(iss_coords['X'])
    Y_iss = np.array(iss_coords['Y'])
    Z_iss = np.array(iss_coords['Z'])
    
    line_plot_iss.set_data(X_iss, Y_iss)
    line_plot_iss.set_3d_properties(Z_iss)
    current_point_iss.set_data([X_iss[-1]], [Y_iss[-1]])
    current_point_iss.set_3d_properties([Z_iss[-1]])
    
    # Adjust axis limits based on view mode
    if view_mode == "satellite":
        margin = 1000  # km
        ax.set_xlim(np.min(X_iss) - margin, np.max(X_iss) + margin)
        ax.set_ylim(np.min(Y_iss) - margin, np.max(Y_iss) + margin)
        ax.set_zlim(np.min(Z_iss) - margin, np.max(Z_iss) + margin)
        moon_artist.set_visible(False)
    elif view_mode == "system":
        ax.set_xlim(-500000, 500000)
        ax.set_ylim(-500000, 500000)
        ax.set_zlim(-500000, 500000)
        moon_artist.set_visible(True)
    
    set_axes_equal(ax)
    ax.view_init(elev=20, azim=30)
    
    current_time_str = datetime.datetime.utcnow().isoformat() + "Z"
    title_str = f"ISS Orbit - {view_mode.capitalize()} View - {current_time_str}\n"
    title_str += f"ISS: ({X_iss[-1]:.2f}, {Y_iss[-1]:.2f}, {Z_iss[-1]:.2f})"
    ax.set_title(title_str)
    
    return line_plot_iss, current_point_iss

def on_key(event):
    global view_mode, latest_coords_iss
    if event.key == 's':
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        if latest_coords_iss is not None:
            filename = f"iss_orbit_{timestamp}.csv"
            try:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Index", "X (km)", "Y (km)", "Z (km)"])
                    for i in range(len(latest_coords_iss['X'])):
                        writer.writerow([i, latest_coords_iss['X'][i],
                                         latest_coords_iss['Y'][i],
                                         latest_coords_iss['Z'][i]])
                print(f"ISS data saved to {filename}")
            except Exception as e:
                print("Error saving ISS data:", e)
    elif event.key == 'v':
        view_mode = "system" if view_mode == "satellite" else "satellite"
        print("Toggled view mode to:", view_mode)

fig.canvas.mpl_connect('key_press_event', on_key)
ani = FuncAnimation(fig, update, interval=10000)
plt.show()
