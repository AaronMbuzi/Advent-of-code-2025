import sys

def main():
    # Read points from input.txt
    points = set()
    try:
        with open('input.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    x_str, y_str = line.split(',')
                    x = int(x_str)
                    y = int(y_str)
                    points.add((x, y))
    except FileNotFoundError:
        print("File 'input.txt' not found.")
        sys.exit(1)
    
    # Convert to list for iteration
    pts = list(points)
    n = len(pts)
    max_area = 0
    
    # Check all pairs of distinct points
    for i in range(n):
        x1, y1 = pts[i]
        for j in range(i+1, n):
            x2, y2 = pts[j]
            width = abs(x1 - x2) + 1
            height = abs(y1 - y2) + 1
            area = width * height
            if area > max_area:
                max_area = area
    
    print(max_area)

if __name__ == "__main__":
    main()