from pathlib import Path

p = Path('input.txt')
data = p.read_text().strip().splitlines()
grid = [list(line.rstrip()) for line in data if line.strip()!='']
h = len(grid)
w = max(len(row) for row in grid) if h>0 else 0
for row in grid:
    row += ['.']*(w-len(row))

dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

total_removed = 0
round_num = 0
while True:
    to_remove = []
    for i in range(h):
        for j in range(w):
            if grid[i][j] == '@':
                cnt = 0
                for di,dj in dirs:
                    ni, nj = i+di, j+dj
                    if 0 <= ni < h and 0 <= nj < w and grid[ni][nj] == '@':
                        cnt += 1
                if cnt < 4:
                    to_remove.append((i,j))
    if not to_remove:
        break
    round_num += 1
    print(f"Round {round_num}: removing {len(to_remove)} rolls")
    total_removed += len(to_remove)
    for i,j in to_remove:
        grid[i][j] = '.'   # remove

print("Total removed:", total_removed)
# optionally print final grid
print("\nFinal grid:")
print("\n".join("".join(row) for row in grid))
