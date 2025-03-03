import sys

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python mandelbrot.py <size>")

    size = int(sys.argv[1])
    w = h = size
    max_iter = 50
    limit = 2.0

    sys.stdout.write(f'P4\n{w} {h}\n')
    sys.stdout.flush()

    for y in range(h):
        byte_acc = 0
        bit_num = 0

        for x in range(w):
            Zr = Zi = Tr = Ti = 0.0
            
            Cr = (2.0 * x / w - 1.5)
            Ci = (2.0 * y / h - 1.0)
            
            for i in range(max_iter):
                if Tr + Ti > limit * limit:
                    break
                Zi = 2.0 * Zr * Zi + Ci
                Zr = Tr - Ti + Cr
                Tr = Zr * Zr
                Ti = Zi * Zi
            
            byte_acc = byte_acc << 1
            if Tr + Ti <= limit * limit:
                byte_acc |= 0x01
            
            bit_num += 1

            if bit_num == 8:
                sys.stdout.buffer.write(bytes([byte_acc]))
                byte_acc = 0
                bit_num = 0
            elif x == w - 1:
                byte_acc = byte_acc << (8 - bit_num)
                sys.stdout.buffer.write(bytes([byte_acc]))
                byte_acc = 0
                bit_num = 0

if __name__ == '__main__':
    main()
