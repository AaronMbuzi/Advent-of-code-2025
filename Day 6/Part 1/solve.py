def solve_day6():
    # Read all lines, keep raw spacing
    lines = [line.rstrip("\n") for line in open("input.txt", "r")]
    if not lines:
        return 0

    height = len(lines)
    width = max(len(line) for line in lines)

    # Normalize line lengths to equal width using spaces
    grid = [line.ljust(width) for line in lines]

    problems = []
    col = 0

    while col < width:
        # Skip columns that are all spaces = separators
        if all(grid[row][col] == " " for row in range(height)):
            col += 1
            continue

        # Now we are inside a problem column-block
        problem_cols = []
        while col < width and not all(grid[row][col] == " " for row in range(height)):
            problem_cols.append(col)
            col += 1

        problems.append(problem_cols)

    total = 0

    for cols in problems:
        numbers = []
        op = None

        # For each row, check if the row contains digits or operation symbol in these columns
        for row in range(height):
            snippet = "".join(grid[row][c] for c in cols).strip()

            if not snippet:
                continue

            if snippet.isdigit():
                numbers.append(int(snippet))
            elif snippet in ("+", "*"):
                op = snippet

        # Evaluate the problem
        if op == "+":
            ans = sum(numbers)
        elif op == "*":
            ans = 1
            for n in numbers:
                ans *= n
        else:
            raise ValueError("Missing operation in problem!")

        total += ans

    print("Grand total:", total)
    return total


if __name__ == "__main__":
    solve_day6()
