import math
from heapq import nsmallest

class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

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
        return True

def dist(a, b):
    return math.sqrt(
        (a[0] - b[0]) ** 2 +
        (a[1] - b[1]) ** 2 +
        (a[2] - b[2]) ** 2
    )

# ---- Read input ----
pts = []
with open("input.txt") as f:
    for line in f:
        if "," in line:
            x, y, z = map(int, line.strip().split(","))
            pts.append((x, y, z))

n = len(pts)
edges = []

# ---- Compute all pair distances ----
for i in range(n):
    for j in range(i + 1, n):
        d = dist(pts[i], pts[j])
        edges.append((d, i, j))

# ---- Select the 1000 smallest distances ----
closest = nsmallest(1000, edges, key=lambda x: x[0])

# ---- Union DSU ----
dsu = DSU(n)
for _, a, b in closest:
    dsu.union(a, b)

# ---- Count circuit sizes ----
components = {}
for i in range(n):
    r = dsu.find(i)
    components.setdefault(r, 0)
    components[r] += 1

sizes = sorted(components.values(), reverse=True)
answer = sizes[0] * sizes[1] * sizes[2]

print("Answer:", answer)
