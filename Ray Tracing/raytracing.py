import math
import numpy as np
from PIL import Image

# Image resolution
width, height = 800, 600

# --- Adjusted Parameters for an "Interstellar-like" Wormhole ---
a = 1.0            # Smaller throat for a concentrated lensing ring
N = 1.0            # Use a positive value for a more controlled effect
dt = -0.005        # Smaller step size for finer detail in raymarching
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

# Utility function: normalize a vector.
def normalize(v):
    norm = math.sqrt(sum(i ** 2 for i in v))
    return [i / norm for i in v] if norm != 0 else v

# Utility function: compute the length of a vector.
def length(v):
    return math.sqrt(sum(i ** 2 for i in v))

# Enhanced texture function for a luminous ring effect.
def texture(channel, coord, brightness):
    # Compute a radial factor from the 2D projection of coord.
    r_coord = math.sqrt(coord[0]**2 + coord[1]**2)
    ringRadius = 0.2
    ringWidth = 0.1
    ringFactor = max(0.0, 1.0 - abs(r_coord - ringRadius) / ringWidth)
    finalBrightness = brightness * ringFactor
    colorValue = int(255 * finalBrightness)
    # Return a nearly white color where the ring is brightest.
    return [colorValue, colorValue, colorValue, 255]

# Main function that computes the color of a single pixel.
def mainImage(fragColor, fragCoord, iResolution, iChannel0, iChannel1):
    # Compute uv coordinates in the range [-1, 1]
    uv = [ (2.0 * fragCoord[0] - iResolution[0]) / iResolution[0],
           (2.0 * fragCoord[1] - iResolution[1]) / iResolution[0] ]
    
    # Construct a 3D ray direction:
    # x-component is -zoom, and y, z come from uv.
    vel = normalize([-zoom] + uv)
    beta = normalize(vel[1:])  # 2D vector from the last two components

    # Initialize ray parameters.
    l = camL
    r = Ltor(l)
    dl = vel[0]
    H = length(vel[1:])
    phi = 0.0
    dr = 0.0
    steps = 0

    # Raymarching loop.
    while abs(l) < max(abs(camL) * 2.0, a + 2.0) and steps < maxSteps:
        dr = LtoDR(l)
        r = Ltor(l)
        # Safeguard against division by zero.
        if abs(r) < 1e-6:
            r = 1e-6

        dx = dl * dr * math.cos(phi) - (H / r) * math.sin(phi)
        dy = dl * dr * math.sin(phi) + (H / r) * math.cos(phi)
        vec = normalize([dx, dy] + beta)

        # Update ray parameters.
        l += dl * dt
        phi += (H / r) * dt
        dl += ((H * H * dr) / (r * r)) * dt
        steps += 1

    # Compute brightness based on the number of steps taken.
    brightness = max(0.0, 1.0 - (steps / maxSteps))
    # Rearrange components to form a direction vector.
    cubeVec = [-vec[0], vec[2], -vec[1]]
    # Set the pixel color using the enhanced texture function.
    fragColor[:] = texture(None, cubeVec, brightness)

# Render the entire image.
def render_image(width, height):
    # Create a 2D list for the image; each pixel is [R, G, B, A].
    image = [[[0, 0, 0, 255] for _ in range(width)] for _ in range(height)]
    iResolution = [width, height]
    iChannel0 = None  # Placeholder texture channel
    iChannel1 = None

    for y in range(height):
        for x in range(width):
            fragColor = [0, 0, 0, 255]
            fragCoord = [x, y]
            mainImage(fragColor, fragCoord, iResolution, iChannel0, iChannel1)
            image[y][x] = fragColor
    return image

# Save the rendered image as a PNG.
def save_image(image, width, height, filename):
    arr = np.array(image, dtype=np.uint8)
    img = Image.fromarray(arr, 'RGBA')
    img.save(filename)

if __name__ == '__main__':
    image = render_image(width, height)
    save_image(image, width, height, 'raytracing_output.png')
    print('Image saved as raytracing_output.png')
