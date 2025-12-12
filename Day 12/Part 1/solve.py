#!/usr/bin/env python3
"""
exact_packing.py

Reads input.txt in the same directory (format described in the puzzle).
Performs:
  - area feasibility check for each region
  - exact packing attempt (Algorithm X) with rotations+flips for each area-feasible region

Outputs:
  - summary: number of regions area-feasible, number actually tileable (found packing within time limit)
  - per-region status printed as progress
"""

from collections import defaultdict
import sys
import time
import math

# -------------------------
# Parsing
# -------------------------
def parse_input(path="input.txt"):
    lines = open(path, "r", encoding="utf8").read().splitlines()
    # First: shapes until first region line (contains 'x' like "12x5:")
    shapes_raw = {}
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if "x" in line and ":" in line and line.split(":")[0].strip().replace("x","").isdigit():
            break
        if ":" in line:
            idx = int(line.split(":")[0])
            i += 1
            grid = []
            # read subsequent non-empty, non-region lines as shape rows
            while i < len(lines):
                if not lines[i].strip():
                    i += 1
                    break
                nxt = lines[i].rstrip("\n")
                # stop if next block is region header (like '12x5:') or another shape start (like '1:')
                if ":" in nxt and nxt.split(":")[0].strip().isdigit() and '[' not in nxt:
                    break
                if "x" in nxt and ":" in nxt and nxt.split(":")[0].strip().replace("x","").isdigit():
                    break
                # shapes lines usually contain '#' or '.'
                if set(nxt.strip()) <= set(".#"):
                    grid.append(nxt.strip())
                    i += 1
                else:
                    # In case of stray formatting, break
                    break
            shapes_raw[idx] = grid
        else:
            i += 1

    # Parse regions from remainder
    regions = []
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if "x" in line and ":" in line:
            dims, rest = line.split(":")
            w_s, h_s = dims.split("x")
            w = int(w_s.strip()); h = int(h_s.strip())
            counts = [int(x) for x in rest.strip().split()]
            regions.append((w, h, counts))
    return shapes_raw, regions


# -------------------------
# Shape normalization + orientations
# -------------------------
def cells_from_grid(grid):
    cells = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == "#":
                cells.append((x, y))
    return tuple(cells)

def normalize(cells):
    minx = min(x for x, y in cells)
    miny = min(y for x, y in cells)
    norm = tuple(sorted(((x - minx, y - miny) for x, y in cells)))
    return norm

def rotate90(cells):
    # (x,y) -> (-y, x)
    return tuple(( -y, x) for x, y in cells)

def reflect_x(cells):
    return tuple((-x, y) for x, y in cells)

def all_orientations(cells):
    """Return sorted list of unique normalized orientations (tuples of (x,y))."""
    seen = set()
    res = []
    base = tuple(cells)
    for flip in (False, True):
        cur = base
        if flip:
            cur = reflect_x(cur)
        # apply 4 rotations
        r = cur
        for _ in range(4):
            r = rotate90(r)
            norm = normalize(r)
            if norm not in seen:
                seen.add(norm)
                res.append(norm)
    return res


# -------------------------
# Exact cover modeling
# -------------------------
# We'll model columns:
#  - one column per grid cell (cx,cy)
#  - one column per piece-instance (we treat identical pieces as separate instances)
#
# Rows:
#  - each possible placement of any piece-instance: covers the instance column + the cell columns it occupies
#
# We'll implement Algorithm X with sets and heuristic choose smallest column.
#

def make_placements_for_region(w, h, pieces_orients_counts):
    """
    pieces_orients_counts: list of (shape_idx, orientations_list, count)
    orientations_list: list of normalized cell tuples
    Returns:
      rows: dict row_id -> set(columns)
      columns: dict col -> set(row_ids)
      instance_cols: list of instance column names (to ensure all instances must be used)
    """
    rows = {}   # row_id -> set(columns)
    columns = defaultdict(set)  # col -> set(row_ids)
    row_id_counter = 0
    instance_cols = []

    # cell column names like ('C', x, y)
    # instance column names like ('P', idx, instance_num)
    # Pre-generate placements
    for shape_idx, orients, count in pieces_orients_counts:
        for inst in range(count):
            inst_col = ('P', shape_idx, inst)
            instance_cols.append(inst_col)
            # for each orientation, try all positions
            for orient in orients:
                # compute bbox of orient
                max_x = max(x for x, y in orient)
                max_y = max(y for x, y in orient)
                for ox in range(0, w - max_x):
                    for oy in range(0, h - max_y):
                        # compute cells covered
                        covered = []
                        valid = True
                        for dx, dy in orient:
                            cx = ox + dx
                            cy = oy + dy
                            if not (0 <= cx < w and 0 <= cy < h):
                                valid = False
                                break
                            covered.append(('C', cx, cy))
                        if not valid:
                            continue
                        rowcols = set(covered)
                        rowcols.add(inst_col)
                        # store row
                        rid = row_id_counter
                        row_id_counter += 1
                        rows[rid] = rowcols
                        for c in rowcols:
                            columns[c].add(rid)
    return rows, columns, instance_cols

# -------------------------
# Algorithm X (recursive) with time limit
# -------------------------
def solve_exact_cover(rows, columns, primary_cols, time_limit=None):
    """
    rows: dict row_id -> set(cols)
    columns: dict col -> set(row_ids)
    primary_cols: iterable/list of columns that must be covered (we require all)
    time_limit: seconds, optional
    Returns True if a cover is found, False otherwise.
    """
    start_time = time.time()
    primary_cols = set(primary_cols)

    # local copies to mutate
    col_to_rows = {c: set(columns.get(c, set())) for c in columns}
    # include primary cols that had no rows -> impossible immediately
    for c in primary_cols:
        if not col_to_rows.get(c):
            return False

    def choose_column():
        # choose uncovered primary column with fewest rows (heuristic)
        best = None
        best_count = None
        for c, rows_for_c in col_to_rows.items():
            # skip columns that are already removed (empty dict entry)
            if rows_for_c is None:
                continue
            if c not in primary_cols:
                continue
            cnt = len(rows_for_c)
            if cnt == 0:
                return None  # dead end
            if best is None or cnt < best_count:
                best = c; best_count = cnt
        return best

    # maintain stack of operations for backtracking:
    def search(k=0):
        # time limit check
        if time_limit is not None and (time.time() - start_time) > time_limit:
            raise TimeoutError()

        # if no remaining primary columns (all covered)
        active_primary = [c for c in primary_cols if col_to_rows.get(c)]
        if not active_primary:
            return True

        c = choose_column()
        if c is None:
            return False

        # iterate copy of rows to avoid mutation issues
        rows_for_c = list(col_to_rows[c])
        for r in rows_for_c:
            # cover r: remove all columns that r covers, and remove all rows that cover those columns
            removed_cols = []
            removed_rows_for_col = {}
            for col in rows[r]:
                # save rows for col for restore
                removed_rows_for_col[col] = col_to_rows.get(col, set()).copy()
                # remove rows that intersect this column
                for rr in list(removed_rows_for_col[col]):
                    # for all cols that row rr covers, remove rr
                    for col2 in rows[rr]:
                        if col2 == col:
                            continue
                        s = col_to_rows.get(col2)
                        if s is not None and rr in s:
                            s.remove(rr)
                # finally mark column as removed by setting to None
                col_to_rows[col] = None
                removed_cols.append(col)

            # recursive
            try:
                if search(k+1):
                    return True
            except TimeoutError:
                # restore and propagate timeout
                # restore columns
                for col in removed_cols:
                    col_to_rows[col] = removed_rows_for_col[col]
                # restore other columns rows removed earlier
                for col, srows in removed_rows_for_col.items():
                    for rr in srows:
                        # re-add rr to other columns it was removed from
                        for col2 in rows[rr]:
                            if col2 != col and col_to_rows.get(col2) is not None:
                                col_to_rows[col2].add(rr)
                raise

            # restore after trying r
            for col in removed_cols:
                col_to_rows[col] = removed_rows_for_col[col]
            for col, srows in removed_rows_for_col.items():
                for rr in srows:
                    for col2 in rows[rr]:
                        if col2 != col and col_to_rows.get(col2) is not None:
                            # rr may already be present, but add is idempotent
                            col_to_rows[col2].add(rr)

        return False

    try:
        return search(0)
    except TimeoutError:
        return None  # indicate timeout

# -------------------------
# Main orchestration
# -------------------------
def main(per_region_timeout=8.0):
    shapes_raw, regions = parse_input("input.txt")
    # convert shapes
    shapes_orients = {}
    shape_areas = {}
    for idx, grid in shapes_raw.items():
        cells = cells_from_grid(grid)
        orients = all_orientations(cells)
        shapes_orients[idx] = orients
        shape_areas[idx] = len(cells)

    total_regions = len(regions)
    area_feasible = []
    for r_idx, (w, h, counts) in enumerate(regions):
        total_area_needed = 0
        for sidx, cnt in enumerate(counts):
            if cnt > 0:
                total_area_needed += shape_areas[sidx] * cnt
        if total_area_needed <= w * h:
            area_feasible.append((r_idx, w, h, counts))

    print(f"Total regions: {total_regions}, area-feasible: {len(area_feasible)}")
    tileable_count = 0
    detailed_results = []

    for (r_idx, w, h, counts) in area_feasible:
        print(f"[Region {r_idx}] {w}x{h}, counts={counts}  ==> building placements...", flush=True)
        pieces = []
        total_needed = 0
        for sidx, cnt in enumerate(counts):
            if cnt > 0:
                pieces.append((sidx, shapes_orients[sidx], cnt))
                total_needed += shape_areas[sidx] * cnt
        # quick sanity
        if total_needed == 0:
            print("  no pieces, trivially fits")
            tileable_count += 1
            detailed_results.append((r_idx, True, 'no pieces'))
            continue

        # Build placements (rows & columns)
        rows, columns, instance_cols = make_placements_for_region(w, h, pieces)
        # primary columns must include all instance columns and all cell columns
        # Determine all cell columns present in 'columns' (those keys starting with 'C')
        cell_cols = [c for c in columns.keys() if c[0] == 'C']
        primary_cols = set(instance_cols) | set(cell_cols)
        # quick check that every instance column has >=1 row
        impossible = False
        for inst in instance_cols:
            if not columns.get(inst):
                impossible = True
                break
        if impossible:
            print("  impossible: an instance has zero placements")
            detailed_results.append((r_idx, False, 'instance_no_placement'))
            continue

        print(f"  placements rows={len(rows)}, columns={len(columns)}; attempting exact cover (timeout {per_region_timeout}s)...", flush=True)

        start = time.time()
        res = solve_exact_cover(rows, columns, primary_cols, time_limit=per_region_timeout)
        took = time.time() - start
        if res is True:
            print(f"  -> TILED in {took:.2f}s")
            tileable_count += 1
            detailed_results.append((r_idx, True, f"time={took:.2f}s"))
        elif res is False:
            print(f"  -> NOT tileable (proved) in {took:.2f}s")
            detailed_results.append((r_idx, False, 'proved_not_tileable'))
        else:
            print(f"  -> TIMEOUT after {took:.2f}s (no solution found within time)")
            detailed_results.append((r_idx, False, 'timeout'))

    print("======================================")
    print(f"Area-feasible regions: {len(area_feasible)}")
    print(f"Tileable regions (within timeout): {tileable_count}")
    print("Detailed summary (first 20 entries):")
    for item in detailed_results[:20]:
        print(" ", item)
    # write full results to a file
    with open("packing_results.txt", "w", encoding="utf8") as out:
        out.write(f"Total regions: {total_regions}\n")
        out.write(f"Area-feasible: {len(area_feasible)}\n")
        out.write(f"Tileable within timeout per-region ({per_region_timeout}s): {tileable_count}\n")
        for r_idx, ok, note in detailed_results:
            out.write(f"{r_idx}\t{ok}\t{note}\n")
    print("Detailed results saved to packing_results.txt")

if __name__ == "__main__":
    timeout = 8.0
    if len(sys.argv) > 1:
        try:
            timeout = float(sys.argv[1])
        except:
            pass
    main(per_region_timeout=timeout)

#!/usr/bin/env python3
"""
exact_packing.py

Reads input.txt in the same directory (format described in the puzzle).
Performs:
  - area feasibility check for each region
  - exact packing attempt (Algorithm X) with rotations+flips for each area-feasible region

Outputs:
  - summary: number of regions area-feasible, number actually tileable (found packing within time limit)
  - per-region status printed as progress
"""

from collections import defaultdict
import sys
import time
import math

# -------------------------
# Parsing
# -------------------------
def parse_input(path="input.txt"):
    lines = open(path, "r", encoding="utf8").read().splitlines()
    # First: shapes until first region line (contains 'x' like "12x5:")
    shapes_raw = {}
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if "x" in line and ":" in line and line.split(":")[0].strip().replace("x","").isdigit():
            break
        if ":" in line:
            idx = int(line.split(":")[0])
            i += 1
            grid = []
            # read subsequent non-empty, non-region lines as shape rows
            while i < len(lines):
                if not lines[i].strip():
                    i += 1
                    break
                nxt = lines[i].rstrip("\n")
                # stop if next block is region header (like '12x5:') or another shape start (like '1:')
                if ":" in nxt and nxt.split(":")[0].strip().isdigit() and '[' not in nxt:
                    break
                if "x" in nxt and ":" in nxt and nxt.split(":")[0].strip().replace("x","").isdigit():
                    break
                # shapes lines usually contain '#' or '.'
                if set(nxt.strip()) <= set(".#"):
                    grid.append(nxt.strip())
                    i += 1
                else:
                    # In case of stray formatting, break
                    break
            shapes_raw[idx] = grid
        else:
            i += 1

    # Parse regions from remainder
    regions = []
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if "x" in line and ":" in line:
            dims, rest = line.split(":")
            w_s, h_s = dims.split("x")
            w = int(w_s.strip()); h = int(h_s.strip())
            counts = [int(x) for x in rest.strip().split()]
            regions.append((w, h, counts))
    return shapes_raw, regions


# -------------------------
# Shape normalization + orientations
# -------------------------
def cells_from_grid(grid):
    cells = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == "#":
                cells.append((x, y))
    return tuple(cells)

def normalize(cells):
    minx = min(x for x, y in cells)
    miny = min(y for x, y in cells)
    norm = tuple(sorted(((x - minx, y - miny) for x, y in cells)))
    return norm

def rotate90(cells):
    # (x,y) -> (-y, x)
    return tuple(( -y, x) for x, y in cells)

def reflect_x(cells):
    return tuple((-x, y) for x, y in cells)

def all_orientations(cells):
    """Return sorted list of unique normalized orientations (tuples of (x,y))."""
    seen = set()
    res = []
    base = tuple(cells)
    for flip in (False, True):
        cur = base
        if flip:
            cur = reflect_x(cur)
        # apply 4 rotations
        r = cur
        for _ in range(4):
            r = rotate90(r)
            norm = normalize(r)
            if norm not in seen:
                seen.add(norm)
                res.append(norm)
    return res


# -------------------------
# Exact cover modeling
# -------------------------
# We'll model columns:
#  - one column per grid cell (cx,cy)
#  - one column per piece-instance (we treat identical pieces as separate instances)
#
# Rows:
#  - each possible placement of any piece-instance: covers the instance column + the cell columns it occupies
#
# We'll implement Algorithm X with sets and heuristic choose smallest column.
#

def make_placements_for_region(w, h, pieces_orients_counts):
    """
    pieces_orients_counts: list of (shape_idx, orientations_list, count)
    orientations_list: list of normalized cell tuples
    Returns:
      rows: dict row_id -> set(columns)
      columns: dict col -> set(row_ids)
      instance_cols: list of instance column names (to ensure all instances must be used)
    """
    rows = {}   # row_id -> set(columns)
    columns = defaultdict(set)  # col -> set(row_ids)
    row_id_counter = 0
    instance_cols = []

    # cell column names like ('C', x, y)
    # instance column names like ('P', idx, instance_num)
    # Pre-generate placements
    for shape_idx, orients, count in pieces_orients_counts:
        for inst in range(count):
            inst_col = ('P', shape_idx, inst)
            instance_cols.append(inst_col)
            # for each orientation, try all positions
            for orient in orients:
                # compute bbox of orient
                max_x = max(x for x, y in orient)
                max_y = max(y for x, y in orient)
                for ox in range(0, w - max_x):
                    for oy in range(0, h - max_y):
                        # compute cells covered
                        covered = []
                        valid = True
                        for dx, dy in orient:
                            cx = ox + dx
                            cy = oy + dy
                            if not (0 <= cx < w and 0 <= cy < h):
                                valid = False
                                break
                            covered.append(('C', cx, cy))
                        if not valid:
                            continue
                        rowcols = set(covered)
                        rowcols.add(inst_col)
                        # store row
                        rid = row_id_counter
                        row_id_counter += 1
                        rows[rid] = rowcols
                        for c in rowcols:
                            columns[c].add(rid)
    return rows, columns, instance_cols

# -------------------------
# Algorithm X (recursive) with time limit
# -------------------------
def solve_exact_cover(rows, columns, primary_cols, time_limit=None):
    """
    rows: dict row_id -> set(cols)
    columns: dict col -> set(row_ids)
    primary_cols: iterable/list of columns that must be covered (we require all)
    time_limit: seconds, optional
    Returns True if a cover is found, False otherwise.
    """
    start_time = time.time()
    primary_cols = set(primary_cols)

    # local copies to mutate
    col_to_rows = {c: set(columns.get(c, set())) for c in columns}
    # include primary cols that had no rows -> impossible immediately
    for c in primary_cols:
        if not col_to_rows.get(c):
            return False

    def choose_column():
        # choose uncovered primary column with fewest rows (heuristic)
        best = None
        best_count = None
        for c, rows_for_c in col_to_rows.items():
            # skip columns that are already removed (empty dict entry)
            if rows_for_c is None:
                continue
            if c not in primary_cols:
                continue
            cnt = len(rows_for_c)
            if cnt == 0:
                return None  # dead end
            if best is None or cnt < best_count:
                best = c; best_count = cnt
        return best

    # maintain stack of operations for backtracking:
    def search(k=0):
        # time limit check
        if time_limit is not None and (time.time() - start_time) > time_limit:
            raise TimeoutError()

        # if no remaining primary columns (all covered)
        active_primary = [c for c in primary_cols if col_to_rows.get(c)]
        if not active_primary:
            return True

        c = choose_column()
        if c is None:
            return False

        # iterate copy of rows to avoid mutation issues
        rows_for_c = list(col_to_rows[c])
        for r in rows_for_c:
            # cover r: remove all columns that r covers, and remove all rows that cover those columns
            removed_cols = []
            removed_rows_for_col = {}
            for col in rows[r]:
                # save rows for col for restore
                removed_rows_for_col[col] = col_to_rows.get(col, set()).copy()
                # remove rows that intersect this column
                for rr in list(removed_rows_for_col[col]):
                    # for all cols that row rr covers, remove rr
                    for col2 in rows[rr]:
                        if col2 == col:
                            continue
                        s = col_to_rows.get(col2)
                        if s is not None and rr in s:
                            s.remove(rr)
                # finally mark column as removed by setting to None
                col_to_rows[col] = None
                removed_cols.append(col)

            # recursive
            try:
                if search(k+1):
                    return True
            except TimeoutError:
                # restore and propagate timeout
                # restore columns
                for col in removed_cols:
                    col_to_rows[col] = removed_rows_for_col[col]
                # restore other columns rows removed earlier
                for col, srows in removed_rows_for_col.items():
                    for rr in srows:
                        # re-add rr to other columns it was removed from
                        for col2 in rows[rr]:
                            if col2 != col and col_to_rows.get(col2) is not None:
                                col_to_rows[col2].add(rr)
                raise

            # restore after trying r
            for col in removed_cols:
                col_to_rows[col] = removed_rows_for_col[col]
            for col, srows in removed_rows_for_col.items():
                for rr in srows:
                    for col2 in rows[rr]:
                        if col2 != col and col_to_rows.get(col2) is not None:
                            # rr may already be present, but add is idempotent
                            col_to_rows[col2].add(rr)

        return False

    try:
        return search(0)
    except TimeoutError:
        return None  # indicate timeout

# -------------------------
# Main orchestration
# -------------------------
def main(per_region_timeout=8.0):
    shapes_raw, regions = parse_input("input.txt")
    # convert shapes
    shapes_orients = {}
    shape_areas = {}
    for idx, grid in shapes_raw.items():
        cells = cells_from_grid(grid)
        orients = all_orientations(cells)
        shapes_orients[idx] = orients
        shape_areas[idx] = len(cells)

    total_regions = len(regions)
    area_feasible = []
    for r_idx, (w, h, counts) in enumerate(regions):
        total_area_needed = 0
        for sidx, cnt in enumerate(counts):
            if cnt > 0:
                total_area_needed += shape_areas[sidx] * cnt
        if total_area_needed <= w * h:
            area_feasible.append((r_idx, w, h, counts))

    print(f"Total regions: {total_regions}, area-feasible: {len(area_feasible)}")
    tileable_count = 0
    detailed_results = []

    for (r_idx, w, h, counts) in area_feasible:
        print(f"[Region {r_idx}] {w}x{h}, counts={counts}  ==> building placements...", flush=True)
        pieces = []
        total_needed = 0
        for sidx, cnt in enumerate(counts):
            if cnt > 0:
                pieces.append((sidx, shapes_orients[sidx], cnt))
                total_needed += shape_areas[sidx] * cnt
        # quick sanity
        if total_needed == 0:
            print("  no pieces, trivially fits")
            tileable_count += 1
            detailed_results.append((r_idx, True, 'no pieces'))
            continue

        # Build placements (rows & columns)
        rows, columns, instance_cols = make_placements_for_region(w, h, pieces)
        # primary columns must include all instance columns and all cell columns
        # Determine all cell columns present in 'columns' (those keys starting with 'C')
        cell_cols = [c for c in columns.keys() if c[0] == 'C']
        primary_cols = set(instance_cols) | set(cell_cols)
        # quick check that every instance column has >=1 row
        impossible = False
        for inst in instance_cols:
            if not columns.get(inst):
                impossible = True
                break
        if impossible:
            print("  impossible: an instance has zero placements")
            detailed_results.append((r_idx, False, 'instance_no_placement'))
            continue

        print(f"  placements rows={len(rows)}, columns={len(columns)}; attempting exact cover (timeout {per_region_timeout}s)...", flush=True)

        start = time.time()
        res = solve_exact_cover(rows, columns, primary_cols, time_limit=per_region_timeout)
        took = time.time() - start
        if res is True:
            print(f"  -> TILED in {took:.2f}s")
            tileable_count += 1
            detailed_results.append((r_idx, True, f"time={took:.2f}s"))
        elif res is False:
            print(f"  -> NOT tileable (proved) in {took:.2f}s")
            detailed_results.append((r_idx, False, 'proved_not_tileable'))
        else:
            print(f"  -> TIMEOUT after {took:.2f}s (no solution found within time)")
            detailed_results.append((r_idx, False, 'timeout'))

    print("======================================")
    print(f"Area-feasible regions: {len(area_feasible)}")
    print(f"Tileable regions (within timeout): {tileable_count}")
    print("Detailed summary (first 20 entries):")
    for item in detailed_results[:20]:
        print(" ", item)
    # write full results to a file
    with open("packing_results.txt", "w", encoding="utf8") as out:
        out.write(f"Total regions: {total_regions}\n")
        out.write(f"Area-feasible: {len(area_feasible)}\n")
        out.write(f"Tileable within timeout per-region ({per_region_timeout}s): {tileable_count}\n")
        for r_idx, ok, note in detailed_results:
            out.write(f"{r_idx}\t{ok}\t{note}\n")
    print("Detailed results saved to packing_results.txt")

if __name__ == "__main__":
    timeout = 8.0
    if len(sys.argv) > 1:
        try:
            timeout = float(sys.argv[1])
        except:
            pass
    main(per_region_timeout=timeout)
