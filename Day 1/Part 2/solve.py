#!/usr/bin/env python3
"""
solve.py

Usage:
    python solve.py input.txt

Reads rotations (one per line, e.g. "L25" or "R1000") and prints:
 - Part 1: number of times the dial is at 0 after a rotation
 - Part 2: number of times the dial is at 0 during any click of the rotations
"""

import sys

def part1_count(rotations, start=50):
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
            raise ValueError(f"Bad instruction: {line}")
        if pos == 0:
            count += 1
    return count

def part2_count(rotations, start=50):
    """
    Count number of times during the clicks of rotations (k = 1..dist) that pos becomes 0.
    For a rotation with direction sgn (+1 for R, -1 for L) and starting pos,
    we need k in 1..dist such that (pos + sgn * k) % 100 == 0.
    Solve for k: k ≡ -sgn*pos (mod 100).
    Let target_k = (-sgn*pos) % 100. If target_k == 0 then the first solution in positive k is 100.
    If target_k > dist -> 0 occurrences. Otherwise occurrences = 1 + (dist - target_k) // 100.
    """
    pos = start
    total = 0
    for line in rotations:
        line = line.strip()
        if not line:
            continue
        dir_ = line[0].upper()
        dist = int(line[1:])
        sgn = 1 if dir_ == 'R' else -1

        # compute target k in 1..100
        target_k = (-sgn * pos) % 100
        if target_k == 0:
            target_k = 100

        if target_k <= dist:
            total += 1 + (dist - target_k) // 100

        # update pos to end position
        if dir_ == 'L':
            pos = (pos - dist) % 100
        else:
            pos = (pos + dist) % 100

    return total

def read_file_lines(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]

def main(argv):
    if len(argv) < 2:
        print("Usage: python solve.py input.txt")
        return
    filename = argv[1]
    rotations = read_file_lines(filename)
    p1 = part1_count(rotations)
    p2 = part2_count(rotations)
    print("Part 1 (count at end of rotations):", p1)
    print("Part 2 (count during rotations):   ", p2)

if __name__ == "__main__":
    main(sys.argv)
