from collections import defaultdict

def parse_input(path="input.txt"):
    graph = defaultdict(list)
    with open(path) as f:
        for line in f:
            node, outs = line.strip().split(":")
            outs = outs.strip()
            if outs:
                graph[node].extend(outs.split())
    return graph

def count_paths_memo(graph, start="svr", end="out", required={"dac","fft"}):
    memo = {}

    def dfs(node, required_remaining):
        key = (node, tuple(sorted(required_remaining)))
        if key in memo:
            return memo[key]
        # Remove node from remaining required if visited
        new_required = set(required_remaining)
        if node in new_required:
            new_required.remove(node)
        if node == end:
            # Only count if all required nodes were visited
            return 1 if not new_required else 0
        total = 0
        for neighbor in graph[node]:
            total += dfs(neighbor, new_required)
        memo[key] = total
        return total

    return dfs(start, required)

if __name__ == "__main__":
    graph = parse_input("input.txt")
    total_paths = count_paths_memo(graph)
    print("Total paths from 'svr' to 'out' visiting both dac and fft:", total_paths)
