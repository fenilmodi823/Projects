import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from packaging import version
from sscws.sscws import SscWs
import datetime
import csv
import numpy as np
from matplotlib.animation import FuncAnimation

# Create an instance of SscWs to access the SSCWS API
ssc = SscWs()

def fetch_iss_data():
    """
    Fetch ISS orbital data for the next hour.
    Returns the data dictionary and the coordinates.
    """
    # Use UTC time for current time and one hour ahead
    start_time = datetime.datetime.utcnow()
    end_time = start_time + datetime.timedelta(hours=1)
    start_iso = start_time.isoformat() + "Z"
    end_iso = end_time.isoformat() + "Z"
    
    try:
        result = ssc.get_locations(['iss'], [start_iso, end_iso])
        print("API result:", result)  # Debug print
        data = result['Data'][0]
        coords = data['Coordinates'][0]
        return data, coords
    except Exception as e:
        print("Error fetching ISS data:", e)
        return None, None

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

# Create a line plot (for the orbit) and a marker (for the current position)
line_plot, = ax.plot([], [], [], label='ISS Orbit', lw=2)
current_point, = ax.plot([], [], [], 'ro', label='Current Position', markersize=8)
ax.legend()

# Variables to store the latest fetched data for logging
latest_data = None
latest_coords = None

def update(frame):
    """
    Animation update function.
    Fetches the latest ISS orbit data, updates the 3D plot, and sets the title.
    """
    global latest_data, latest_coords
    data, coords = fetch_iss_data()
    if data is None or coords is None:
        return line_plot, current_point

    latest_data = data
    latest_coords = coords
    
    # Convert coordinate lists to NumPy arrays
    X = np.array(coords['X'])
    Y = np.array(coords['Y'])
    Z = np.array(coords['Z'])

    # Set axis limits so the full orbit is visible
    ax.set_xlim(np.min(X) - 100, np.max(X) + 100)
    ax.set_ylim(np.min(Y) - 100, np.max(Y) + 100)
    ax.set_zlim(np.min(Z) - 100, np.max(Z) + 100)
    
    # Optionally set a fixed view angle (elevation and azimuth)
    ax.view_init(elev=20, azim=30)

    
    # Update the line plot with the full orbit segment
    line_plot.set_data(X, Y)
    line_plot.set_3d_properties(Z)
    
    # Update the marker for the current position (using the last coordinate in the segment)
    current_point.set_data([X[-1]], [Y[-1]])
    current_point.set_3d_properties([Z[-1]])
    
    # Update plot title with current time and the latest ISS position details
    current_time = datetime.datetime.utcnow().isoformat() + "Z"
    ax.set_title(
        f"ISS Orbit - Current Time: {current_time}\n"
        f"Current Position: ({X[-1]:.2f}, {Y[-1]:.2f}, {Z[-1]:.2f})"
    )
    
    return line_plot, current_point

def on_key(event):
    """
    Event handler for key press events.
    Press 's' to save the latest fetched orbital data to a CSV file.
    """
    if event.key == 's':
        if latest_coords is not None:
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            filename = f"iss_orbit_{timestamp}.csv"
            try:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Index", "X (km)", "Y (km)", "Z (km)"])
                    X = latest_coords['X']
                    Y = latest_coords['Y']
                    Z = latest_coords['Z']
                    for i in range(len(X)):
                        writer.writerow([i, X[i], Y[i], Z[i]])
                print(f"Data successfully saved to {filename}")
            except Exception as e:
                print("Error saving data:", e)
        else:
            print("No data available to save yet.")

# Connect the key press event to our on_key function
fig.canvas.mpl_connect('key_press_event', on_key)

# Set up the animation to update the plot every 10 seconds (10000 milliseconds)
ani = FuncAnimation(fig, update, interval=10000)

# Display the interactive 3D plot window
plt.show()
