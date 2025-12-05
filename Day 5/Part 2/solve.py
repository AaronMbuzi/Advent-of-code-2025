def parse_range(line):
    start, end = map(int, line.split("-"))
    return (start, end)

def merge_ranges(ranges):
    # Sort by start value
    ranges.sort(key=lambda x: x[0])
    merged = []

    for r in ranges:
        if not merged or r[0] > merged[-1][1] + 1:
            # No overlap
            merged.append([r[0], r[1]])
        else:
            # Overlap → extend end if needed
            merged[-1][1] = max(merged[-1][1], r[1])

    return merged

def main():
    ranges = []

    with open("input.txt", "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                break  # Stop at blank line
            ranges.append(parse_range(line))

    merged = merge_ranges(ranges)

    total_fresh = sum((end - start + 1) for start, end in merged)

    print("Total fresh ingredient IDs (Part Two):", total_fresh)

if __name__ == "__main__":
    main()
