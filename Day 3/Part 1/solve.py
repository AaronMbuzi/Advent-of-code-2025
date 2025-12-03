def find_max_two_digit_number(digits_str):
    """Return the largest two-digit number formed by two digits in order."""
    digits = [int(ch) for ch in digits_str]
    max_val = -1
    n = len(digits)
    
    for i in range(n - 1):
        first = digits[i]
        # Find the largest digit after i
        max_after = max(digits[i + 1:])
        value = 10 * first + max_after
        if value > max_val:
            max_val = value
    
    return max_val

def main():
    total = 0
    
    # Read from input.txt
    with open('input.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            max_val = find_max_two_digit_number(line)
            total += max_val
    
    print(total)

if __name__ == "__main__":
    main()
def find_max_two_digit_number(digits_str):
    """Return the largest two-digit number formed by two digits in order."""
    digits = [int(ch) for ch in digits_str]
    max_val = -1
    n = len(digits)
    
    for i in range(n - 1):
        first = digits[i]
        # Find the largest digit after i
        max_after = max(digits[i + 1:])
        value = 10 * first + max_after
        if value > max_val:
            max_val = value
    
    return max_val

def main():
    total = 0
    
    # Read from input.txt
    with open('input.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            max_val = find_max_two_digit_number(line)
            total += max_val
    
    print(total)

if __name__ == "__main__":
    main()