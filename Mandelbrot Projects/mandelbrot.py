import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

def mandelbrot_row(row, width, height, x_min, x_max, y_min, y_max, max_iter):
    
    y = y_min + (y_max - y_min) * row / (height - 1)
    x = np.linspace(x_min, x_max, width)
    c = x + 1j * y
    z = np.zeros(c.shape, dtype=np.complex128)
    
    output = np.full(c.shape, max_iter, dtype=int)
    
    for i in range(max_iter):
        mask = np.abs(z) <= 2.0
        z[mask] = z[mask] ** 2 + c[mask]
        diverged = mask & (np.abs(z) > 2.0)
        output[diverged] = i
    return output

def compute_mandelbrot(width=800, height=600, x_min=-2.0, x_max=1.0, y_min=-1.0, y_max=1.0, max_iter=256):
    args = [
        (row, width, height, x_min, x_max, y_min, y_max, max_iter)
        for row in range(height)
    ]
    with Pool(cpu_count()) as pool:
        result = pool.starmap(mandelbrot_row, args)
    return np.array(result)

if __name__ == '__main__':
    width = 1200
    height = 800
    max_iter = 1024
    x_min, x_max = -2.0, 1.0
    y_min, y_max = -1.0, 1.0

    mandelbrot_image = compute_mandelbrot(width, height, x_min, x_max, y_min, y_max, max_iter)
    
    plt.figure(figsize=(10, 8))
    plt.imshow(mandelbrot_image, extent=(x_min, x_max, y_min, y_max),
               cmap='hot', origin='lower')
    plt.colorbar(label='Iteration count')
    plt.title("Mandelbrot Set")
    plt.xlabel("Real Axis")
    plt.ylabel("Imaginary Axis")
    plt.show()
