def count_zeros(rotations, start=50):
    pos = start
    count = 0
    for line in rotations:
        line = line.strip()
        if not line:
            continue
        dir_ = line[0].upper()
        dist = int(line[1:])

        if dir_ == 'L':
            pos = (pos - dist) % 100
        elif dir_ == 'R':
            pos = (pos + dist) % 100
        else:
            raise ValueError("Invalid instruction: " + line)

        if pos == 0:
            count += 1

    return count


# ---- READ FROM FILE HERE ----
filename = "input.txt"   # change if needed

with open(filename, "r") as f:
    rotations = f.read().strip().splitlines()

password = count_zeros(rotations)
print("Password:", password)
