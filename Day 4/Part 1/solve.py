from pathlib import Path

p = Path('input.txt')
data = p.read_text().strip().splitlines()
grid = [list(line.rstrip()) for line in data if line.strip()!='']
h = len(grid)
w = max(len(row) for row in grid) if h>0 else 0
for row in grid:
    row += ['.']*(w-len(row))

dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
accessible = []
for i in range(h):
    for j in range(w):
        if grid[i][j]=='@':
            cnt = 0
            for di,dj in dirs:
                ni,nj = i+di, j+dj
                if 0<=ni<h and 0<=nj<w and grid[ni][nj]=='@':
                    cnt += 1
            if cnt < 4:
                accessible.append((i,j))

print("Accessible count:", len(accessible))
# optional: print marked grid
out = [row.copy() for row in grid]
for i,j in accessible:
    out[i][j] = 'x'
print("\n".join("".join(row) for row in out))

from pathlib import Path

p = Path('input.txt')
data = p.read_text().strip().splitlines()
grid = [list(line.rstrip()) for line in data if line.strip()!='']
h = len(grid)
w = max(len(row) for row in grid) if h>0 else 0
for row in grid:
    row += ['.']*(w-len(row))

dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
accessible = []
for i in range(h):
    for j in range(w):
        if grid[i][j]=='@':
            cnt = 0
            for di,dj in dirs:
                ni,nj = i+di, j+dj
                if 0<=ni<h and 0<=nj<w and grid[ni][nj]=='@':
                    cnt += 1
            if cnt < 4:
                accessible.append((i,j))

print("Accessible count:", len(accessible))
# optional: print marked grid
out = [row.copy() for row in grid]
for i,j in accessible:
    out[i][j] = 'x'
print("\n".join("".join(row) for row in out))
