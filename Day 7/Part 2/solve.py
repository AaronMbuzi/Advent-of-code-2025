from collections import deque, defaultdict

def read_grid(path="input.txt"):
    with open(path, "r") as f:
        lines = [line.rstrip("\n") for line in f]
    if not lines:
        return [], 0, 0
    H = len(lines)
    W = max(len(l) for l in lines)
    grid = [l.ljust(W, " ") for l in lines]
    return grid, H, W

def find_start(grid, H, W):
    for r in range(H):
        c = grid[r].find("S")
        if c != -1:
            return (r + 1, c)   # beam/particle begins just below S
    raise ValueError("No S found in input")

def outgoing(cell, grid, H, W):
    """Return list of neighbor cells (r,c) inside grid, and count of edges that go out-of-bounds."""
    r, c = cell
    # If current cell itself is out of bounds - caller shouldn't ask this, treat as no outgoing.
    if not (0 <= r < H and 0 <= c < W):
        return [], 0

    ch = grid[r][c]
    outs = []
    exits = 0

    if ch == "^":
        # splitter: spawns to immediate left and right on the same row
        for nc in (c - 1, c + 1):
            if 0 <= nc < W:
                outs.append((r, nc))
            else:
                exits += 1
    else:
        # normal: continues downward
        nr, nc = r + 1, c
        if 0 <= nr < H and 0 <= nc < W:
            outs.append((nr, nc))
        else:
            exits += 1

    return outs, exits

def build_graph_and_reachable(start, grid, H, W):
    """BFS to find reachable nodes and build adjacency and exit-edge counts."""
    q = deque([start])
    seen = set([start])
    adj = defaultdict(list)
    exit_edges = defaultdict(int)  # exit_edges[node] = number of edges from node that go out-of-bounds

    while q:
        node = q.popleft()
        nbrs, exits = outgoing(node, grid, H, W)
        exit_edges[node] = exits
        for v in nbrs:
            adj[node].append(v)
            if v not in seen:
                seen.add(v)
                q.append(v)

    return adj, exit_edges, seen

def detect_cycle(adj, nodes):
    """Detect cycle in directed graph restricted to 'nodes' using DFS (white/gray/black)."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}

    def dfs(u):
        color[u] = GRAY
        for v in adj.get(u, ()):
            if v not in color:
                continue
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    for n in nodes:
        if color[n] == WHITE:
            if dfs(n):
                return True
    return False

def count_timelines(path="input.txt"):
    grid, H, W = read_grid(path)
    if H == 0:
        return 0

    start = find_start(grid, H, W)
    adj, exit_edges, nodes = build_graph_and_reachable(start, grid, H, W)

    # If no nodes (start might be out of bounds), then zero timelines
    if not nodes:
        return 0

    # detect cycles (would imply infinite timelines)
    if detect_cycle(adj, nodes):
        raise RuntimeError("Cycle detected in reachable graph: timelines would be infinite.")

    # Topological order (Kahn). Compute indegrees for reachable subgraph.
    indeg = {n: 0 for n in nodes}
    for u in nodes:
        for v in adj.get(u, ()):
            if v in indeg:
                indeg[v] += 1

    # Kahn's queue
    q = deque([n for n in nodes if indeg[n] == 0])
    topo = []
    while q:
        u = q.popleft()
        topo.append(u)
        for v in adj.get(u, ()):
            if v in indeg:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)

    # DP: number of ways to reach each node (big integers)
    ways = defaultdict(int)
    ways[start] = 1
    total_exits = 0

    # Process nodes in topological order and propagate
    for u in topo:
        w = ways[u]
        # edges that go out-of-bounds contribute to final timelines
        if exit_edges.get(u, 0):
            total_exits += w * exit_edges[u]
        for v in adj.get(u, ()):
            ways[v] += w

    return total_exits

if __name__ == "__main__":
    result = count_timelines("input.txt")
    print("Total timelines:", result)
