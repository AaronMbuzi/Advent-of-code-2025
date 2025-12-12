# day10_factory_solver.py
import re
import sys

# -----------------------
# GF(2) Gaussian elimination producing:
# - a particular solution (if exists)
# - basis vectors for the nullspace (free-variable directions)
# Rows = equations (lights), Columns = variables (buttons)
# -----------------------

def parse_machine_line(line):
    # expects a line like:
    # [.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
    lights_match = re.search(r'\[([.#]+)\]', line)
    if not lights_match:
        raise ValueError("No lights pattern found")
    lights = lights_match.group(1).strip()
    target = [1 if c == '#' else 0 for c in lights]
    # find all parenthesized button specs
    buttons = re.findall(r'\(([0-9, ]*)\)', line)
    btn_list = []
    for b in buttons:
        b = b.strip()
        if b == "":
            # empty button toggles nothing
            btn_list.append([])
        else:
            indices = [int(x.strip()) for x in b.split(',') if x.strip() != ""]
            btn_list.append(indices)
    return target, btn_list

def build_matrix(target, btn_list):
    m = len(target)   # number of lights (equations)
    n = len(btn_list) # number of buttons (variables)
    # Represent matrix as list of ints where bit j corresponds to column j
    A = [0] * m
    for j, indices in enumerate(btn_list):
        for i in indices:
            if i < 0 or i >= m:
                raise ValueError(f"Button references invalid light index {i}")
            A[i] |= (1 << j)
    b = 0
    for i, val in enumerate(target):
        if val:
            b |= (1 << i)
    return A, b, m, n

def gaussian_elim(A_in, b_in, m, n):
    # Work on copies
    A = A_in[:]  # A[i] is an int with bits for columns
    b = b_in
    row = 0
    pivot_cols = [-1] * m  # pivot_cols[row] = col index if pivot at that row
    col_to_row = {}  # map pivot_col -> row
    for col in range(n):
        # find a row >= row with bit col set
        sel = None
        for r in range(row, m):
            if (A[r] >> col) & 1:
                sel = r
                break
        if sel is None:
            continue
        # swap sel row into 'row'
        if sel != row:
            A[sel], A[row] = A[row], A[sel]
            # swap corresponding bits of b: we store b as bitmask of rows
            bit_sel = (b >> sel) & 1
            bit_row = (b >> row) & 1
            if bit_sel != bit_row:
                # flip both bits
                b ^= (1 << sel) | (1 << row)
        # now eliminate other rows that have bit col
        for r in range(m):
            if r != row and ((A[r] >> col) & 1):
                A[r] ^= A[row]
                # flip b bit if needed
                if ((b >> row) & 1):
                    b ^= (1 << r)
        pivot_cols[row] = col
        col_to_row[col] = row
        row += 1
        if row == m:
            break

    rank = row

    # Check for inconsistency: rows with all-zero A but b bit = 1
    for r in range(rank, m):
        if A[r] == 0 and ((b >> r) & 1):
            return None  # no solution

    # Build a particular solution x0 (length n) as int bitmask for variables
    x0 = 0
    # For each pivot row, the pivot column value equals the right-hand side (since other pivot cols eliminated)
    for r in range(rank):
        c = pivot_cols[r]
        if c == -1:
            continue
        # the row corresponds to A[r] having 1 at col c and possibly some non-pivot columns
        # But after elimination other pivot columns cleared; remaining columns are free variables
        val = (b >> r) & 1
        if val:
            x0 |= (1 << c)

    # Construct nullspace basis: For each free column fcol, create vector v where v[fcol]=1 and
    # for each pivot row r, v[pivot_col] = value required to cancel pivot when free var is 1
    free_cols = []
    pivot_col_set = set(col_to_row.keys())
    for col in range(n):
        if col not in pivot_col_set:
            free_cols.append(col)
    null_basis = []
    # For each free column, set that free column to 1 and compute pivot variable bits from rows
    for fcol in free_cols:
        vec = 0
        vec |= (1 << fcol)
        # For each pivot row r with pivot column pc, if A[r] has 1 in fcol then pivot variable must flip
        for r in range(rank):
            pc = pivot_cols[r]
            if ((A[r] >> fcol) & 1):
                vec |= (1 << pc)
        null_basis.append(vec)

    return x0, null_basis, free_cols

# Gray code enumeration for nullspace search
def min_weight_solution_by_enumeration(x0, basis):
    f = len(basis)
    if f == 0:
        # unique solution
        return x0.bit_count(), x0
    # precompute basis as integers
    basis = list(basis)
    # Gray code iteration: for i from 0..2^f-1, gray = i ^ (i>>1)
    best_weight = None
    best_x = None
    cur = 0  # current xor of selected basis vectors
    prev_gray = 0
    max_iter = 1 << f
    for i in range(max_iter):
        gray = i ^ (i >> 1)
        diff = gray ^ prev_gray
        if diff:
            # find index of changed bit
            idx = (diff.bit_length() - 1)
            cur ^= basis[idx]
        x = x0 ^ cur
        w = x.bit_count()
        if (best_weight is None) or (w < best_weight):
            best_weight = w
            best_x = x
            # small optimization: if weight is 0, can't beat
            if best_weight == 0:
                break
        prev_gray = gray
    return best_weight, best_x

# Fallback local search when too many free vars:
def min_weight_solution_local_search(x0, basis, iterations=200000):
    # greedy hill-climb randomized: start at x0 then flip random combination of basis vectors to reduce weight
    import random
    f = len(basis)
    best_x = x0
    best_w = x0.bit_count()
    # start with zero combination
    cur_combo = 0
    cur_x = x0
    # try random single-bit flips in basis
    for it in range(iterations):
        idx = random.randrange(f)
        new_x = cur_x ^ basis[idx]
        new_w = new_x.bit_count()
        if new_w < best_w:
            best_w = new_w
            best_x = new_x
        # accept move if better or with small probability (simulated annealing not implemented)
        if new_w <= cur_x.bit_count() or random.random() < 0.001:
            cur_x = new_x
    return best_w, best_x

def solve_machine_line(line, verbose=False):
    target, btn_list = parse_machine_line(line)
    A, b, m, n = build_matrix(target, btn_list)
    res = gaussian_elim(A, b, m, n)
    if res is None:
        raise ValueError("Machine has no solution (inconsistent)")
    x0, null_basis, free_cols = res
    f = len(null_basis)
    if verbose:
        print(f"Lights={m}, Buttons={n}, Rank={n - f if n>0 else 0}, Free={f}")
    # choose strategy
    if f <= 26:
        weight, x = min_weight_solution_by_enumeration(x0, null_basis)
    else:
        # fallback local search; warn user
        if verbose:
            print("Warning: many free variables (f=%d); using local search fallback" % f)
        weight, x = min_weight_solution_local_search(x0, null_basis)
    return weight, x

def solve_file(path="input.txt", verbose=False):
    total = 0
    per_machine = []
    with open(path, "r") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                weight, x = solve_machine_line(line, verbose=verbose)
            except Exception as e:
                print(f"Error solving line {lineno}: {e}")
                raise
            total += weight
            per_machine.append((lineno, weight))
            if verbose:
                print(f"Line {lineno}: min presses = {weight}")
    return total, per_machine

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", default="input.txt")
    p.add_argument("--verbose", "-v", action="store_true")
    args = p.parse_args()
    tot, details = solve_file(args.input, verbose=args.verbose)
    print("Total minimal presses across all machines:", tot)
    if args.verbose:
        for ln, w in details:
            print(f"  line {ln}: {w}")
