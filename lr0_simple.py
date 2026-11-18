"""
Practical: LR(0) Parser Check (Canonical Collection & Conflict Detection)
Description:
    Augments the grammar, creates the canonical collection of LR(0) items (Closure & Goto),
    checks for Shift-Reduce (SR) and Reduce-Reduce (RR) conflicts, and determines if the grammar is LR(0).
"""

def get_symbols(productions, non_terminals):
    terminals = set()
    for _, rhs in productions:
        for ch in rhs:
            if not ch.isupper() and ch != '#':
                terminals.add(ch)
    return non_terminals, sorted(list(terminals))

def closure(items, productions, non_terminals):
    # An item is a tuple: (prod_index, dot_position)
    closure_set = set(items)
    changed = True
    while changed:
        changed = False
        new_items = set()
        for prod_idx, dot in closure_set:
            lhs, rhs = productions[prod_idx]
            if dot < len(rhs):
                sym = rhs[dot]
                if sym in non_terminals:
                    for i, (p_lhs, p_rhs) in enumerate(productions):
                        if p_lhs == sym:
                            item = (i, 0)
                            if item not in closure_set:
                                new_items.add(item)
        if new_items:
            closure_set.update(new_items)
            changed = True
    return tuple(sorted(list(closure_set)))

def goto(state_items, symbol, productions, non_terminals):
    moved = set()
    for prod_idx, dot in state_items:
        lhs, rhs = productions[prod_idx]
        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((prod_idx, dot + 1))
    if not moved:
        return ()
    return closure(moved, productions, non_terminals)

def format_item(item, productions):
    prod_idx, dot = item
    lhs, rhs = productions[prod_idx]
    dotted = rhs[:dot] + "." + rhs[dot:]
    return f"{lhs} -> {dotted}"

def main():
    print("=" * 60)
    print("          LR(0) GRAMMAR CHECK & CANONICAL ITEMS")
    print("=" * 60)
    print("Default Grammar: ")
    print("  E -> a A | b B")
    print("  A -> c")
    print("  B -> c")
    print("-" * 60)
    use_default = input("Use default grammar? (Y/n): ").strip().lower()

    if use_default == 'n':
        n = int(input("Enter number of productions: "))
        raw_lines = [input().strip() for _ in range(n)]
    else:
        # Classic example to test LR(0)
        raw_lines = [
            "S->AA",
            "A->aA",
            "A->b"
        ]

    # Parse grammar
    productions = []
    non_terminals = []
    for line in raw_lines:
        line = line.strip().replace(" ", "")
        if "->" not in line:
            continue
        lhs, rhs = line.split("->", 1)
        if lhs not in non_terminals:
            non_terminals.append(lhs)
        for part in rhs.split("|"):
            productions.append((lhs, part))

    # Augment grammar with S' -> S
    start = non_terminals[0]
    augmented_start = start + "'" if start + "'" not in non_terminals else "Z"
    productions.insert(0, (augmented_start, start))
    non_terminals.insert(0, augmented_start)

    _, terminals = get_symbols(productions, non_terminals)
    all_symbols = [nt for nt in non_terminals if nt != augmented_start] + terminals

    # Build canonical states
    initial_item = (0, 0)
    i0 = closure([initial_item], productions, non_terminals)
    states = [i0]
    transitions = {}

    queue = [0]
    while queue:
        current_idx = queue.pop(0)
        current_state = states[current_idx]
        for sym in all_symbols:
            nxt = goto(current_state, sym, productions, non_terminals)
            if nxt:
                if nxt not in states:
                    states.append(nxt)
                    queue.append(len(states) - 1)
                dest_idx = states.index(nxt)
                transitions[(current_idx, sym)] = dest_idx

    # Print canonical collection of items
    print(f"\nCanonical Collection of LR(0) Items: ({len(states)} states)")
    for i, state in enumerate(states):
        print(f"\n--- State I{i} ---")
        for itm in state:
            print("  " + format_item(itm, productions))

    # Check for conflicts
    # In LR(0), for any state:
    # If there is a reduction (dot at the end), it reduces on ALL terminals + '$'.
    # If there are shifts as well -> Shift-Reduce conflict.
    # If there are multiple reductions -> Reduce-Reduce conflict.
    has_sr_conflict = False
    has_rr_conflict = False

    for i, state in enumerate(states):
        shifts = []
        reductions = []
        for prod_idx, dot in state:
            lhs, rhs = productions[prod_idx]
            if dot == len(rhs):
                reductions.append((prod_idx, lhs, rhs))
            else:
                next_sym = rhs[dot]
                if next_sym in terminals:
                    shifts.append(next_sym)

        # Check RR conflict
        if len(reductions) > 1:
            has_rr_conflict = True
            print(f"\n[!] Reduce-Reduce Conflict in State I{i}:")
            for r in reductions:
                print(f"    Reduce by {r[1]} -> {r[2]}")

        # Check SR conflict
        if len(reductions) >= 1 and len(shifts) > 0:
            # Note: S' -> S. is accept, not normal reduction
            normal_reductions = [r for r in reductions if r[0] != 0]
            if normal_reductions and shifts:
                has_sr_conflict = True
                print(f"\n[!] Shift-Reduce Conflict in State I{i}:")
                print(f"    Shifts on: {shifts}")
                for r in normal_reductions:
                    print(f"    Reduce by {r[1]} -> {r[2]}")

    print("\n" + "=" * 50)
    if not has_sr_conflict and not has_rr_conflict:
        print("RESULT: Grammar is LR(0) (No SR or RR conflicts found).")
    else:
        print("RESULT: Grammar is NOT LR(0) due to conflicts.")
    print("=" * 50)

if __name__ == "__main__":
    main()

