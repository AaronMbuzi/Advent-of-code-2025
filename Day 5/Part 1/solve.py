def parse_range(line):
    """Parse a 'start-end' string into a tuple of ints."""
    start, end = line.split("-")
    return int(start), int(end)

def is_fresh(id_value, ranges):
    """Check if id_value falls within ANY of the ranges."""
    for low, high in ranges:
        if low <= id_value <= high:
            return True
    return False

def main():
    ranges = []
    ids = []

    with open("input.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip() != ""]

    # Find first line that is NOT a range -> that starts the IDs
    idx = 0
    while idx < len(lines) and "-" in lines[idx]:
        ranges.append(parse_range(lines[idx]))
        idx += 1

    # Remaining lines are ingredient IDs
    for i in range(idx, len(lines)):
        ids.append(int(lines[i]))

    # Count fresh IDs
    fresh_count = sum(1 for value in ids if is_fresh(value, ranges))

    print("Total fresh ingredient IDs:", fresh_count)


if __name__ == "__main__":
    main()
