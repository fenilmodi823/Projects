import numpy as np
import matplotlib.pyplot as plt

def mandelbrot(c, max_iter=100):
    z = 0
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z**2 + c
    return max_iter

def generate_mandelbrot(xmin, xmax, ymin, ymax, width, height, max_iter=100):
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    mandelbrot_set = np.zeros((height, width))
    
    for i in range(height):
        for j in range(width):
            c = complex(x[j], y[i])
            mandelbrot_set[i, j] = mandelbrot(c, max_iter)
    
    return mandelbrot_set

xmin, xmax, ymin, ymax = -2.0, 1.0, -1.5, 1.5
width, height = 1000, 1000
max_iter = 200

mandelbrot_image = generate_mandelbrot(xmin, xmax, ymin, ymax, width, height, max_iter)

plt.figure(figsize=(10, 10))
plt.imshow(mandelbrot_image, extent=(xmin, xmax, ymin, ymax), cmap='inferno', origin='lower')
plt.colorbar(label='Iterations')
plt.title('Mandelbrot Set')
plt.xlabel('Real Part')
plt.ylabel('Imaginary Part')
plt.show()
