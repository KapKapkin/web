import random
import math

def circle_square_mk(r, n):
    count = 0
    for _ in range(n):
        x = random.uniform(-r, r)
        y = random.uniform(-r, r)
        if x**2 + y**2 <= r**2:
            count += 1
    return (2*r)**2 * count / n

if __name__ == '__main__':
    r = 1
    n = 1000000
    mk_area = circle_square_mk(r, n)
    real_area = math.pi * r**2
    print(f"Монте-Карло: {mk_area:.6f}")
    print(f"Формула: {real_area:.6f}")
    print(f"Погрешность: {abs(mk_area - real_area)/real_area*100:.2f}%")
