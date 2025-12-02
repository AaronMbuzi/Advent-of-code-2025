def parse_ranges(ranges_str):
    rngs = []
    for part in ranges_str.split(","):
        part = part.strip()
        if not part:
            continue
        a, b = part.split("-")
        rngs.append((int(a), int(b)))
    return rngs

def generate_repeated_numbers(max_value):
    max_digits = len(str(max_value))
    found = set()
    # base length l from 1..max_digits-1 (must repeat at least twice)
    for l in range(1, max_digits):
        start = 10**(l-1)
        end = 10**l - 1
        max_k = max_digits // l
        if max_k < 2:
            continue
        for s in range(start, end+1):
            base = str(s)
            for k in range(2, max_k+1):
                n = int(base * k)
                if n > max_value:
                    break
                found.add(n)
    return found

def sum_invalid_ids_part2_from_file(filename):
    with open(filename, "r") as f:
        ranges_str = f.read().strip()
    ranges = parse_ranges(ranges_str)
    max_end = max(b for _, b in ranges)
    repeated = generate_repeated_numbers(max_end)
    found = set()
    for n in repeated:
        for a, b in ranges:
            if a <= n <= b:
                found.add(n)
                break
    return sum(found), len(found)

if __name__ == "__main__":
    total, count = sum_invalid_ids_part2_from_file("input.txt")
    print(total)
    # print("count:", count)

def parse_ranges(ranges_str):
    rngs = []
    for part in ranges_str.split(","):
        part = part.strip()
        if not part:
            continue
        a, b = part.split("-")
        rngs.append((int(a), int(b)))
    return rngs

def generate_repeated_numbers(max_value):
    max_digits = len(str(max_value))
    found = set()
    # base length l from 1..max_digits-1 (must repeat at least twice)
    for l in range(1, max_digits):
        start = 10**(l-1)
        end = 10**l - 1
        max_k = max_digits // l
        if max_k < 2:
            continue
        for s in range(start, end+1):
            base = str(s)
            for k in range(2, max_k+1):
                n = int(base * k)
                if n > max_value:
                    break
                found.add(n)
    return found

def sum_invalid_ids_part2_from_file(filename):
    with open(filename, "r") as f:
        ranges_str = f.read().strip()
    ranges = parse_ranges(ranges_str)
    max_end = max(b for _, b in ranges)
    repeated = generate_repeated_numbers(max_end)
    found = set()
    for n in repeated:
        for a, b in ranges:
            if a <= n <= b:
                found.add(n)
                break
    return sum(found), len(found)

if __name__ == "__main__":
    total, count = sum_invalid_ids_part2_from_file("input.txt")
    print(total)
    # print("count:", count)
