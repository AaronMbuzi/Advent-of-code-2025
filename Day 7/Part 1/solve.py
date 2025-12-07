from collections import deque

def count_splits_from_file(path="input.txt"):
    # Read grid (preserve spacing)
    with open(path, "r") as f:
        lines = [line.rstrip("\n") for line in f]
    if not lines:
        return 0

    H = len(lines)
    W = max(len(l) for l in lines)
    grid = [l.ljust(W, " ") for l in lines]

    # find S
    S_row = S_col = None
    for r in range(H):
        c = grid[r].find("S")
        if c != -1:
            S_row, S_col = r, c
            break
    if S_row is None:
        raise ValueError("No S found in input")

    # BFS/stack of beam positions (row, col) representing the current cell the beam occupies
    start = (S_row + 1, S_col)  # beam begins directly below S
    queue = deque([start])

    visited = set()            # cells we've already processed for a beam
    splitters_counted = set()  # splitter coordinates we've already counted
    splits = 0

    while queue:
        r, c = queue.popleft()

        # out of bounds or already processed
        if not (0 <= c < W and 0 <= r < H):
            continue
        if (r, c) in visited:
            continue
        visited.add((r, c))

        ch = grid[r][c]

        # treat spaces as empty (beam passes through until it goes off-grid)
        if ch == "^":
            # beam hits splitter: it stops here, and spawns new beams immediately
            if (r, c) not in splitters_counted:
                splits += 1
                splitters_counted.add((r, c))
            # spawn left and right beams starting at the same row (immediate left/right of splitter)
            left = (r, c - 1)
            right = (r, c + 1)
            if 0 <= left[1] < W:
                queue.append(left)
            if 0 <= right[1] < W:
                queue.append(right)
        else:
            # empty / S / . / space: beam continues downward
            queue.append((r + 1, c))

    return splits

if __name__ == "__main__":
    result = count_splits_from_file("input.txt")
    print("Total beam splits:", result)
