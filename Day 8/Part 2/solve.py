# day8_part2.py
import sys
from math import inf

class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1]*n
        self.components = n

    def find(self, x):
        while x != self.parent[x]:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.components -= 1
        return True

def read_points(path="input.txt"):
    pts = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "," in line:
                x,y,z = map(int, line.split(","))
                pts.append((x,y,z))
    return pts

def squared_dist(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2

def find_last_connection_product(path="input.txt"):
    pts = read_points(path)
    n = len(pts)
    if n <= 1:
        print("Not enough points.")
        return None

    # Build all edges (squared distance, i, j)
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            d2 = squared_dist(pts[i], pts[j])
            edges.append((d2, i, j))

    # Sort edges by distance (ascending)
    edges.sort(key=lambda x: x[0])

    dsu = DSU(n)
    last_pair = None

    for d2, i, j in edges:
        merged = dsu.union(i, j)
        if merged:
            # this union decreased component count
            last_pair = (i, j)
            if dsu.components == 1:
                # this was the edge that connected everything
                x1 = pts[i][0]
                x2 = pts[j][0]
                product = x1 * x2
                print("Last connection merged indices:", i, j)
                print("Coordinates:", pts[i], pts[j])
                print("Product of X coordinates:", product)
                return product

    # If we finish and components > 1 (shouldn't happen), return None
    print("Warning: graph did not become fully connected.")
    return None

if __name__ == "__main__":
    find_last_connection_product("input.txt")
