def find_max_m_digit_number(digits_str, m=12):
    """Return the largest m-digit number formed by m digits in order."""
    digits = [int(ch) for ch in digits_str]
    n = len(digits)
    if n < m:
        return 0  # Not enough digits, but problem likely gives enough
    
    result_digits = []
    start = 0
    
    for pick in range(m):
        # We need to leave (m - pick - 1) digits after chosen one
        end = n - (m - pick - 1)
        # Find max in range [start, end)
        max_digit = -1
        max_pos = start
        for pos in range(start, end):
            if digits[pos] > max_digit:
                max_digit = digits[pos]
                max_pos = pos
        result_digits.append(max_digit)
        start = max_pos + 1
    
    # Convert list of digits to integer
    total = 0
    for d in result_digits:
        total = total * 10 + d
    return total

def main():
    total = 0
    m = 12
    
    with open('input.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            max_val = find_max_m_digit_number(line, m)
            total += max_val
    
    print(total)

if __name__ == "__main__":
    main()