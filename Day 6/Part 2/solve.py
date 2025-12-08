<<<<<<< HEAD
def solve_day6_part2():
    lines = [line.rstrip("\n") for line in open("input.txt", "r")]
    height = len(lines)
    width = max(len(line) for line in lines)

    # Pad all lines to uniform width
    grid = [line.ljust(width) for line in lines]

    # Identify column groups (problems)
    problems = []
    col = 0
    while col < width:
        # Skip separator columns
        if all(grid[r][col] == " " for r in range(height)):
            col += 1
            continue

        # Now inside a problem-block
        block = []
        while col < width and not all(grid[r][col] == " " for r in range(height)):
            block.append(col)
            col += 1

        problems.append(block)

    total = 0

    for block in problems:
        # Reverse block columns (read right → left)
        block = list(reversed(block))

        digits_per_number = []
        op = None

        # Determine operator in the bottom row for this block
        bottom_row = height - 1
        snippet = "".join(grid[bottom_row][c] for c in block).strip()
        op = snippet  # must be '+' or '*'

        # Extract the columns above the operator row
        rows_for_digits = range(0, bottom_row)

        # Build numbers column-by-column (right→left)
        numbers = []
        for col_idx in range(len(block)):
            column = block[col_idx]

            digits = []
            for r in rows_for_digits:
                ch = grid[r][column]
                if ch.isdigit():
                    digits.append(ch)

            if digits:
                number = int("".join(digits))
                numbers.append(number)

        # Evaluate problem
        if op == "+":
            value = sum(numbers)
        elif op == "*":
            value = 1
            for n in numbers:
                value *= n
        else:
            raise ValueError("Invalid operator: " + op)

        total += value

    print("Grand total (Part Two):", total)
    return total


if __name__ == "__main__":
    solve_day6_part2()
=======
def solve_day6_part2():
    lines = [line.rstrip("\n") for line in open("input.txt", "r")]
    height = len(lines)
    width = max(len(line) for line in lines)

    # Pad all lines to uniform width
    grid = [line.ljust(width) for line in lines]

    # Identify column groups (problems)
    problems = []
    col = 0
    while col < width:
        # Skip separator columns
        if all(grid[r][col] == " " for r in range(height)):
            col += 1
            continue

        # Now inside a problem-block
        block = []
        while col < width and not all(grid[r][col] == " " for r in range(height)):
            block.append(col)
            col += 1

        problems.append(block)

    total = 0

    for block in problems:
        # Reverse block columns (read right → left)
        block = list(reversed(block))

        digits_per_number = []
        op = None

        # Determine operator in the bottom row for this block
        bottom_row = height - 1
        snippet = "".join(grid[bottom_row][c] for c in block).strip()
        op = snippet  # must be '+' or '*'

        # Extract the columns above the operator row
        rows_for_digits = range(0, bottom_row)

        # Build numbers column-by-column (right→left)
        numbers = []
        for col_idx in range(len(block)):
            column = block[col_idx]

            digits = []
            for r in rows_for_digits:
                ch = grid[r][column]
                if ch.isdigit():
                    digits.append(ch)

            if digits:
                number = int("".join(digits))
                numbers.append(number)

        # Evaluate problem
        if op == "+":
            value = sum(numbers)
        elif op == "*":
            value = 1
            for n in numbers:
                value *= n
        else:
            raise ValueError("Invalid operator: " + op)

        total += value

    print("Grand total (Part Two):", total)
    return total


if __name__ == "__main__":
    solve_day6_part2()
>>>>>>> e0b85b5 (init)
