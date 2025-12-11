import re
import pulp

def parse_machine_line_joltage(line):
    buttons = re.findall(r'\(([0-9, ]*)\)', line)
    btn_list = []
    for b in buttons:
        b = b.strip()
        if b == "":
            btn_list.append([])
        else:
            indices = [int(x.strip()) for x in b.split(',') if x.strip() != ""]
            btn_list.append(indices)
    target_match = re.search(r'\{([0-9, ]*)\}', line)
    if not target_match:
        raise ValueError("No target found")
    target = [int(x.strip()) for x in target_match.group(1).split(',') if x.strip() != ""]
    return btn_list, target

def min_presses_ilp(btn_list, target):
    n_buttons = len(btn_list)
    n_counters = len(target)
    
    # Define LP problem
    prob = pulp.LpProblem("MinButtonPresses", pulp.LpMinimize)
    
    # Variables: number of presses for each button
    x = [pulp.LpVariable(f"x{i}", lowBound=0, cat="Integer") for i in range(n_buttons)]
    
    # Constraints: sum of button contributions equals target for each counter
    for i in range(n_counters):
        prob += pulp.lpSum(x[j] if i in btn_list[j] else 0 for j in range(n_buttons)) == target[i]
    
    # Objective: minimize total button presses
    prob += pulp.lpSum(x)
    
    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    return int(pulp.value(prob.objective))

def solve_file_joltage_ilp(path="input.txt"):
    total = 0
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            btn_list, target = parse_machine_line_joltage(line)
            presses = min_presses_ilp(btn_list, target)
            total += presses
    return total

if __name__ == "__main__":
    ans = solve_file_joltage_ilp("input.txt")
    print("Part Two answer (min total presses for joltage):", ans)
