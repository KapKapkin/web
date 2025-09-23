import math

class Complex:
    def __init__(self, real, imaginary):
        self.real = real
        self.imaginary = imaginary

    def __add__(self, other):
        return Complex(self.real + other.real, self.imaginary + other.imaginary)

    def __sub__(self, other):
        return Complex(self.real - other.real, self.imaginary - other.imaginary)

    def __mul__(self, other):
        real = self.real * other.real - self.imaginary * other.imaginary
        imaginary = self.real * other.imaginary + self.imaginary * other.real
        return Complex(real, imaginary)

    def __truediv__(self, other):
        denominator = other.real**2 + other.imaginary**2
        real = (self.real * other.real + self.imaginary * other.imaginary) / denominator
        imaginary = (self.imaginary * other.real - self.real * other.imaginary) / denominator
        return Complex(real, imaginary)

    def mod(self):
        return Complex(math.sqrt(self.real**2 + self.imaginary**2), 0)

    def __str__(self):
        if self.imaginary == 0:
            return f"{self.real:.2f}+0.00i"
        elif self.real == 0:
            return f"0.00+{self.imaginary:.2f}i"
        else:
            operator = "+" if self.imaginary >= 0 else "-"
            return f"{self.real:.2f}{operator}{abs(self.imaginary):.2f}i"

if __name__ == '__main__':
    a, b = map(float, input().split())
    c, d = map(float, input().split())
    C = Complex(a, b)
    D = Complex(c, d)

    print(C + D)
    print(C - D)
    print(C * D)
    print(C / D)
    print(C.mod())
    print(D.mod())
