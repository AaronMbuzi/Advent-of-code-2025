import java.util.*;
import java.io.*;

public class solve {
    static class Point {
        long x, y;
        Point(long x, long y) {
            this.x = x;
            this.y = y;
        }
    }
    
    public static void main(String[] args) throws IOException {
        // Read from input.txt file in the same directory
        BufferedReader br = new BufferedReader(new FileReader("input.txt"));
        List<Point> points = new ArrayList<>();
        String line;
        while ((line = br.readLine()) != null && !line.isEmpty()) {
            String[] parts = line.split(",");
            long x = Long.parseLong(parts[0]);
            long y = Long.parseLong(parts[1]);
            points.add(new Point(x, y));
        }
        br.close();
        
        System.out.println(solveProblem(points));
    }
    
    static long solveProblem(List<Point> points) {
        int n = points.size();
        if (n == 0) return 0;
        
        // Close the polygon
        List<Point> polygon = new ArrayList<>(points);
        polygon.add(points.get(0));
        
        // Collect unique x and y coordinates
        TreeSet<Long> xSet = new TreeSet<>();
        TreeSet<Long> ySet = new TreeSet<>();
        for (Point p : points) {
            xSet.add(p.x);
            ySet.add(p.y);
        }
        
        List<Long> xs = new ArrayList<>(xSet);
        List<Long> ys = new ArrayList<>(ySet);
        int nx = xs.size();
        int ny = ys.size();
        
        // Mappings from coordinate to index
        Map<Long, Integer> xToIdx = new HashMap<>();
        Map<Long, Integer> yToIdx = new HashMap<>();
        for (int i = 0; i < nx; i++) xToIdx.put(xs.get(i), i);
        for (int i = 0; i < ny; i++) yToIdx.put(ys.get(i), i);
        
        // Build vertical edges
        List<Edge> verticalEdges = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            Point p1 = polygon.get(i);
            Point p2 = polygon.get(i + 1);
            if (p1.x == p2.x) {
                long y1 = p1.y;
                long y2 = p2.y;
                if (y1 > y2) {
                    long temp = y1;
                    y1 = y2;
                    y2 = temp;
                }
                verticalEdges.add(new Edge(p1.x, y1, y2));
            }
        }
        
        // For each y interval, collect x-coordinates of vertical edges that span it
        List<List<Long>> intervalXs = new ArrayList<>(ny - 1);
        for (int i = 0; i < ny - 1; i++) {
            intervalXs.add(new ArrayList<>());
        }
        
        for (Edge e : verticalEdges) {
            int j1 = yToIdx.get(e.y1);
            int j2 = yToIdx.get(e.y2);
            for (int j = j1; j < j2; j++) {
                intervalXs.get(j).add(e.x);
            }
        }
        
        for (int j = 0; j < ny - 1; j++) {
            Collections.sort(intervalXs.get(j));
        }
        
        // Determine which grid cells are inside the polygon
        int[][] allowed = new int[nx - 1][ny - 1];
        for (int i = 0; i < nx - 1; i++) {
            double xc = (xs.get(i) + xs.get(i + 1)) / 2.0;
            for (int j = 0; j < ny - 1; j++) {
                List<Long> lst = intervalXs.get(j);
                // Binary search for first index with x > xc
                int lo = 0, hi = lst.size();
                while (lo < hi) {
                    int mid = (lo + hi) / 2;
                    if (lst.get(mid) > xc) {
                        hi = mid;
                    } else {
                        lo = mid + 1;
                    }
                }
                int cnt = lst.size() - lo;
                allowed[i][j] = (cnt % 2 == 1) ? 1 : 0;
            }
        }
        
        // 2D prefix sums
        long[][] prefix = new long[nx][ny];
        for (int i = 1; i < nx; i++) {
            for (int j = 1; j < ny; j++) {
                prefix[i][j] = allowed[i-1][j-1] + prefix[i-1][j] + prefix[i][j-1] - prefix[i-1][j-1];
            }
        }
        
        // Check all pairs of red points
        long maxArea = 0;
        for (int a = 0; a < n; a++) {
            Point p1 = points.get(a);
            long x1 = p1.x, y1 = p1.y;
            for (int b = a + 1; b < n; b++) {
                Point p2 = points.get(b);
                long x2 = p2.x, y2 = p2.y;
                if (x1 == x2 || y1 == y2) continue;
                
                long xl = Math.min(x1, x2), xr = Math.max(x1, x2);
                long yb = Math.min(y1, y2), yt = Math.max(y1, y2);
                
                int i1 = xToIdx.get(xl);
                int i2 = xToIdx.get(xr);
                int j1 = yToIdx.get(yb);
                int j2 = yToIdx.get(yt);
                
                if (i2 == i1 || j2 == j1) continue;
                
                long cellArea = (long)(i2 - i1) * (j2 - j1);
                long totalAllowed = prefix[i2][j2] - prefix[i1][j2] - prefix[i2][j1] + prefix[i1][j1];
                
                if (totalAllowed == cellArea) {
                    long area = (xr - xl + 1) * (yt - yb + 1);
                    if (area > maxArea) {
                        maxArea = area;
                    }
                }
            }
        }
        
        return maxArea;
    }
    
    static class Edge {
        long x, y1, y2;
        Edge(long x, long y1, long y2) {
            this.x = x;
            this.y1 = y1;
            this.y2 = y2;
        }
    }
}