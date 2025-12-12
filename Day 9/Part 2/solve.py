# Do not use this code, use the Java Code


import sys

def solve(input_str):
    lines = input_str.strip().splitlines()
    points = [tuple(map(int, line.split(','))) for line in lines]
    n = len(points)

    # Close the polygon
    polygon = points + [points[0]]

    # Unique sorted x and y coordinates
    xs = sorted({p[0] for p in points})
    ys = sorted({p[1] for p in points})
    nx = len(xs)
    ny = len(ys)

    # Mappings from coordinate to index
    x_to_idx = {x: i for i, x in enumerate(xs)}
    y_to_idx = {y: i for i, y in enumerate(ys)}

    # Build vertical edges (for ray casting)
    vertical_edges = []
    for i in range(n):
        (x1, y1), (x2, y2) = polygon[i], polygon[i+1]
        if x1 == x2:
            if y1 > y2:
                y1, y2 = y2, y1
            vertical_edges.append((x1, y1, y2))

    # For each interval between consecutive y's, collect x-coordinates of vertical edges that span it
    interval_xs = [[] for _ in range(ny-1)]
    for x, y1, y2 in vertical_edges:
        j1 = y_to_idx[y1]
        j2 = y_to_idx[y2]
        for j in range(j1, j2):   # intervals j with ys[j] < ys[j+1] inside [y1,y2]
            interval_xs[j].append(x)

    for j in range(ny-1):
        interval_xs[j].sort()

    # Determine which grid cells are entirely inside the polygon
    # Cell (i,j) corresponds to x in [xs[i], xs[i+1]] and y in [ys[j], ys[j+1]]
    allowed = [[0]*(ny-1) for _ in range(nx-1)]
    for i in range(nx-1):
        xc = (xs[i] + xs[i+1]) / 2.0
        for j in range(ny-1):
            # Count how many vertical edges to the right of xc in this y-interval
            lst = interval_xs[j]
            # Use binary search to find first index with x > xc
            lo, hi = 0, len(lst)
            while lo < hi:
                mid = (lo + hi) // 2
                if lst[mid] > xc:
                    hi = mid
                else:
                    lo = mid + 1
            cnt = len(lst) - lo
            allowed[i][j] = 1 if cnt % 2 == 1 else 0

    # 2D prefix sums for allowed cells
    prefix = [[0]*(ny) for _ in range(nx)]
    for i in range(1, nx):
        for j in range(1, ny):
            prefix[i][j] = allowed[i-1][j-1] + prefix[i-1][j] + prefix[i][j-1] - prefix[i-1][j-1]

    # Check all pairs of red points
    max_area = 0
    for a in range(n):
        x1, y1 = points[a]
        for b in range(a+1, n):
            x2, y2 = points[b]
            if x1 == x2 or y1 == y2:
                continue   # skip degenerate rectangles (lines)
            xl, xr = min(x1, x2), max(x1, x2)
            yb, yt = min(y1, y2), max(y1, y2)
            i1 = x_to_idx[xl]
            i2 = x_to_idx[xr]
            j1 = y_to_idx[yb]
            j2 = y_to_idx[yt]
            if i2 == i1 or j2 == j1:
                continue   # no cell area
            # Cells from i1 to i2-1, j1 to j2-1
            cell_area = (i2 - i1) * (j2 - j1)
            total_allowed = (prefix[i2][j2] - prefix[i1][j2] -
                             prefix[i2][j1] + prefix[i1][j1])
            if total_allowed == cell_area:
                area = (xr - xl + 1) * (yt - yb + 1)
                if area > max_area:
                    max_area = area

    return max_area

if __name__ == "__main__":
    # Read from file if provided, otherwise from stdin
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            input_str = f.read()
    else:
        input_str = sys.stdin.read()
    print(solve(input_str))