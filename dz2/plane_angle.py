import math

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def cross(self, other):
        return Point(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

def plane_angle(A, B, C, D):
    AB = B - A
    BC = C - B
    CD = D - C

    X = AB.cross(BC)
    Y = BC.cross(CD)

    cos_phi = X.dot(Y) / (X.magnitude() * Y.magnitude())
    return math.degrees(math.acos(cos_phi))
