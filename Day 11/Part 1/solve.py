from collections import defaultdict

def parse_input(path="input.txt"):
    graph = defaultdict(list)
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(":")
            node = parts[0].strip()
            if len(parts) > 1:
                outputs = parts[1].strip().split()
                graph[node].extend(outputs)
    return graph

def count_paths(graph, start="you", end="out"):
    memo = {}  # Memoization to avoid recomputation

    def dfs(node):
        if node == end:
            return 1
        if node in memo:
            return memo[node]
        total = 0
        for neighbor in graph[node]:
            total += dfs(neighbor)
        memo[node] = total
        return total

    return dfs(start)

if __name__ == "__main__":
    graph = parse_input("input.txt")
    total_paths = count_paths(graph)
    print("Total paths from 'you' to 'out':", total_paths)
