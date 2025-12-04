def parse_ranges(ranges_str):
    ranges = []
    for part in ranges_str.split(","):
        part = part.strip()
        if not part:
            continue
        a, b = part.split("-")
        ranges.append((int(a), int(b)))
    return ranges


def generate_double_numbers(max_value):
    # "double numbers" are numbers formed as S+S (e.g., "12"+"12" = 1212)
    max_digits = len(str(max_value))
    doubles = []

    # total length = 2*l, so S has length l
    for l in range(1, max_digits // 2 + 1):
        start = 10 ** (l - 1)
        end = 10 ** l - 1
        for s in range(start, end + 1):
            n = int(str(s) + str(s))
            if n > max_value:
                break
            doubles.append(n)
    return doubles


def sum_invalid_ids_from_file(filename):
    # read file
    with open(filename, "r") as f:
        ranges_str = f.read().strip()

    ranges = parse_ranges(ranges_str)
    max_end = max(b for _, b in ranges)

    # all double numbers up to max_end
    doubles = generate_double_numbers(max_end)

    # collect all invalid numbers that fall in ANY range
    found = set()

    for n in doubles:
        for a, b in ranges:
            if a <= n <= b:
                found.add(n)
                break

    return sum(found)


if __name__ == "__main__":
    result = sum_invalid_ids_from_file("input.txt")
    print(result)
