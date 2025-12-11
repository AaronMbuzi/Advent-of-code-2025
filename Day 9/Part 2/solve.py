import sys

def read_points(filename):
    """Read points from file, maintaining order"""
    points = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                x_str, y_str = line.split(',')
                x = int(x_str)
                y = int(y_str)
                points.append((x, y))
    return points

def get_points_on_line(p1, p2):
    """Get all integer points on the line between p1 and p2 (inclusive)"""
    x1, y1 = p1
    x2, y2 = p2
    points = []
    
    if x1 == x2:  # Vertical line
        y_start, y_end = sorted([y1, y2])
        for y in range(y_start, y_end + 1):
            points.append((x1, y))
    elif y1 == y2:  # Horizontal line
        x_start, x_end = sorted([x1, x2])
        for x in range(x_start, x_end + 1):
            points.append((x, y1))
    
    return points

def is_point_inside_polygon(x, y, polygon, horizontal_edges, vertical_edges):
    """Check if point is inside polygon using even-odd rule"""
    # Check if point is on boundary
    for x1, y1, x2, y2 in horizontal_edges:
        if y == y1 == y2 and min(x1, x2) <= x <= max(x1, x2):
            return True
    for x1, y1, x2, y2 in vertical_edges:
        if x == x1 == x2 and min(y1, y2) <= y <= max(y1, y2):
            return True
    
    # Even-odd rule
    inside = False
    n = len(polygon)
    
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        
        # Check if edge crosses horizontal line at y
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside
    
    return inside

def main():
    # Read polygon points in order
    polygon = read_points('input.txt')
    red_points = set(polygon)
    
    # Get all edges
    n = len(polygon)
    horizontal_edges = []
    vertical_edges = []
    
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        
        if y1 == y2:  # Horizontal edge
            horizontal_edges.append((x1, y1, x2, y2))
        else:  # Vertical edge
            vertical_edges.append((x1, y1, x2, y2))
    
    # Find bounding box
    min_x = min(p[0] for p in polygon)
    max_x = max(p[0] for p in polygon)
    min_y = min(p[1] for p in polygon)
    max_y = max(p[1] for p in polygon)
    
    # Create grid with offset for 0-based indexing
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    
    # Mark allowed cells (red or green)
    allowed = [[0] * width for _ in range(height)]
    
    # Mark red points
    for x, y in red_points:
        allowed[y - min_y][x - min_x] = 1
    
    # Mark green boundary points
    for x1, y1, x2, y2 in horizontal_edges:
        x_start, x_end = sorted([x1, x2])
        for x in range(x_start, x_end + 1):
            allowed[y1 - min_y][x - min_x] = 1
    
    for x1, y1, x2, y2 in vertical_edges:
        y_start, y_end = sorted([y1, y2])
        for y in range(y_start, y_end + 1):
            allowed[y - min_y][x1 - min_x] = 1
    
    # Mark interior green points using flood fill
    # First find a point inside the polygon to start flood fill
    start_x, start_y = None, None
    
    # Try to find a point that's not on boundary but inside
    for y in range(min_y, max_y + 1):
        found = False
        for x in range(min_x, max_x + 1):
            if allowed[y - min_y][x - min_x] == 0 and is_point_inside_polygon(x, y, polygon, horizontal_edges, vertical_edges):
                start_x, start_y = x, y
                found = True
                break
        if found:
            break
    
    if start_x is not None:
        # Flood fill interior
        stack = [(start_x, start_y)]
        while stack:
            x, y = stack.pop()
            if allowed[y - min_y][x - min_x] == 0:
                allowed[y - min_y][x - min_x] = 1
                # Check neighbors
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    if min_x <= nx <= max_x and min_y <= ny <= max_y:
                        if allowed[ny - min_y][nx - min_x] == 0:
                            stack.append((nx, ny))
    
    # Build prefix sum for O(1) rectangle checks
    prefix = [[0] * (width + 1) for _ in range(height + 1)]
    for y in range(height):
        for x in range(width):
            prefix[y + 1][x + 1] = (prefix[y + 1][x] + prefix[y][x + 1] - 
                                  prefix[y][x] + allowed[y][x])
    
    def sum_region(x1, y1, x2, y2):
        """Sum of allowed values in rectangle [x1, x2] x [y1, y2] (inclusive)"""
        return (prefix[y2 + 1][x2 + 1] - prefix[y1][x2 + 1] - 
                prefix[y2 + 1][x1] + prefix[y1][x1])
    
    # Find largest valid rectangle
    max_area = 0
    
    for i in range(n):
        x1, y1 = polygon[i]
        for j in range(i + 1, n):
            x2, y2 = polygon[j]
            
            # Convert to grid coordinates
            gx1 = min(x1, x2) - min_x
            gx2 = max(x1, x2) - min_x
            gy1 = min(y1, y2) - min_y
            gy2 = max(y1, y2) - min_y
            
            # Calculate area
            area = (gx2 - gx1 + 1) * (gy2 - gy1 + 1)
            
            # Check if all cells in rectangle are allowed
            if sum_region(gx1, gy1, gx2, gy2) == area:
                if area > max_area:
                    max_area = area
    
    print(max_area)

if __name__ == "__main__":
    main()