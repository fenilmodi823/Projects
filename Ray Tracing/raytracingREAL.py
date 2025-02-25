import math
import numpy as np
from PIL import Image

# Image resolution
width, height = 800, 600

# --- Adjusted Parameters for an "Interstellar-like" Wormhole ---
a = 1.0            # Smaller throat for a concentrated lensing ring
N = 1.0            # Use a positive value for controlled curvature
dt = -0.005        # Smaller step size for finer raymarching detail
maxSteps = 3000    # Allow more steps for a detailed simulation
camL = 2.0         # Closer camera for a zoomed-in effect
zoom = 2.5         # Higher zoom factor to exaggerate lensing
PI = math.pi

# Wormhole function r(l)
def Ltor(l):
    kappa = max(0.0, 2.0 * (abs(l) - a) / (PI * N))
    return a * a * math.tan(kappa) - 0.5 * math.log(1.0 + kappa * kappa)

# Wormhole derivative
def LtoDR(l):
    x = max(0.0, 2.0 * (abs(l) - a) / (PI * N))
    return a / (1.0 + x * x)

# Utility: Normalize a vector.
def normalize(v):
    norm = math.sqrt(sum(i**2 for i in v))
    return [i / norm for i in v] if norm != 0 else v

# Utility: Compute vector length.
def length(v):
    return math.sqrt(sum(i**2 for i in v))

# Enhanced texture function with accretion disk effect.
def texture(channel, coord, brightness):
    # Compute radial coordinate for the wormhole ring effect.
    r_coord = math.sqrt(coord[0]**2 + coord[1]**2)
    ringRadius = 0.2
    ringWidth = 0.1
    ringFactor = max(0.0, 1.0 - abs(r_coord - ringRadius) / ringWidth)
    
    # Accretion disk effect: assume the disk is visible when the vertical component is small.
    diskThreshold = 0.1
    # Here we assume coord[1] represents the vertical direction.
    diskFactor = max(0.0, 1.0 - abs(coord[1]) / diskThreshold)
    
    # Separate brightness contributions.
    ringBrightness = brightness * ringFactor
    diskBrightness = brightness * diskFactor

    # Define colors:
    # Wormhole ring: nearly white (high intensity).
    ringColor = [ringBrightness * 255, ringBrightness * 255, ringBrightness * 255, 255]
    # Accretion disk: a bright orange-yellow.
    diskColor = [255, 200, 100, 255]
    
    # Blend the two effects using diskFactor as the weighting.
    finalColor = [
        int(ringColor[i] * (1 - diskFactor) + diskColor[i] * diskFactor)
        for i in range(4)
    ]
    return finalColor

# Main image function: computes the color for a single pixel.
def mainImage(fragColor, fragCoord, iResolution, iChannel0, iChannel1):
    # Compute UV coordinates in the range [-1, 1]
    uv = [(2.0 * fragCoord[0] - iResolution[0]) / iResolution[0],
          (2.0 * fragCoord[1] - iResolution[1]) / iResolution[0]]
    
    # Construct a 3D ray direction: x is -zoom, y and z come from uv.
    vel = normalize([-zoom] + uv)
    beta = normalize(vel[1:])
    
    # Initialize ray parameters.
    l = camL
    r = Ltor(l)
    dl = vel[0]
    H = length(vel[1:])
    phi = 0.0
    dr = 0.0
    steps = 0

    # Raymarching loop.
    while abs(l) < max(abs(camL)*2.0, a + 2.0) and steps < maxSteps:
        dr = LtoDR(l)
        r = Ltor(l)
        if abs(r) < 1e-6:
            r = 1e-6
        dx = dl * dr * math.cos(phi) - (H / r) * math.sin(phi)
        dy = dl * dr * math.sin(phi) + (H / r) * math.cos(phi)
        vec = normalize([dx, dy] + beta)
        l += dl * dt
        phi += (H / r) * dt
        dl += ((H * H * dr) / (r * r)) * dt
        steps += 1

    # Compute brightness based on steps (fewer steps = brighter)
    brightness = max(0.0, 1.0 - (steps / maxSteps))
    # Rearranging components into a directional vector.
    cubeVec = [-vec[0], vec[2], -vec[1]]
    # Set pixel color using the enhanced texture function.
    fragColor[:] = texture(None, cubeVec, brightness)

# Render the complete image.
def render_image(width, height):
    image = [[[0, 0, 0, 255] for _ in range(width)] for _ in range(height)]
    iResolution = [width, height]
    iChannel0 = None  # Placeholder for additional texture channels
    iChannel1 = None

    for y in range(height):
        for x in range(width):
            fragColor = [0, 0, 0, 255]
            fragCoord = [x, y]
            mainImage(fragColor, fragCoord, iResolution, iChannel0, iChannel1)
            image[y][x] = fragColor
    return image

# Save the rendered image as a PNG file.
def save_image(image, width, height, filename):
    arr = np.array(image, dtype=np.uint8)
    img = Image.fromarray(arr, 'RGBA')
    img.save(filename)

if __name__ == '__main__':
    image = render_image(width, height)
    save_image(image, width, height, 'raytracing_output.png')
    print('Image saved as raytracing_output.png')
