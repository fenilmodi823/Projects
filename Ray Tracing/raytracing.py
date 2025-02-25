import math
import numpy as np
from PIL import Image

width, height = 800, 600

a = 1.0
N = 1.0
dt = -0.005
maxSteps = 3000
camL = 2.0
zoom = 2.5
PI = math.pi

def Ltor(l):
    kappa = max(0.0, 2.0 * (abs(l) - a) / (PI * N))
    return a * a * math.tan(kappa) - 0.5 * math.log(1.0 + kappa * kappa)

def LtoDR(l):
    x = max(0.0, 2.0 * (abs(l) - a) / (PI * N))
    return a / (1.0 + x * x)

def normalize(v):
    norm = math.sqrt(sum(i ** 2 for i in v))
    return [i / norm for i in v] if norm != 0 else v

def length(v):
    return math.sqrt(sum(i ** 2 for i in v))

def texture(channel, coord, brightness):
    r_coord = math.sqrt(coord[0]**2 + coord[1]**2)
    ringRadius = 0.2
    ringWidth = 0.1
    ringFactor = max(0.0, 1.0 - abs(r_coord - ringRadius) / ringWidth)
    finalBrightness = brightness * ringFactor
    colorValue = int(255 * finalBrightness)
    return [colorValue, colorValue, colorValue, 255]

def mainImage(fragColor, fragCoord, iResolution, iChannel0, iChannel1):
    uv = [ (2.0 * fragCoord[0] - iResolution[0]) / iResolution[0],
           (2.0 * fragCoord[1] - iResolution[1]) / iResolution[0] ]
    
    vel = normalize([-zoom] + uv)
    beta = normalize(vel[1:])

    l = camL
    r = Ltor(l)
    dl = vel[0]
    H = length(vel[1:])
    phi = 0.0
    dr = 0.0
    steps = 0

    while abs(l) < max(abs(camL) * 2.0, a + 2.0) and steps < maxSteps:
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

    brightness = max(0.0, 1.0 - (steps / maxSteps))
    cubeVec = [-vec[0], vec[2], -vec[1]]
    fragColor[:] = texture(None, cubeVec, brightness)

def render_image(width, height):
    image = [[[0, 0, 0, 255] for _ in range(width)] for _ in range(height)]
    iResolution = [width, height]
    iChannel0 = None
    iChannel1 = None

    for y in range(height):
        for x in range(width):
            fragColor = [0, 0, 0, 255]
            fragCoord = [x, y]
            mainImage(fragColor, fragCoord, iResolution, iChannel0, iChannel1)
            image[y][x] = fragColor
    return image

def save_image(image, width, height, filename):
    arr = np.array(image, dtype=np.uint8)
    img = Image.fromarray(arr, 'RGBA')
    img.save(filename)

if __name__ == '__main__':
    image = render_image(width, height)
    save_image(image, width, height, 'raytracing_output.png')
    print('Image successfully saved as raytracing_output.png')
