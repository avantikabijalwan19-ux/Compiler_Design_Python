"""
Practical: SLR(1) Grammar Verification (Simple LR Parser Conflict Analysis)
Description:
    Computes FIRST & FOLLOW sets, generates canonical LR(0) collection of items,
    and checks if the grammar is SLR(1) by placing reductions only in the FOLLOW
    set of the reducing non-terminal.
"""

from first_follow import compute_first, compute_follow
from lr0_parser import closure, goto, get_symbols, format_item

def main():
    print("=" * 60)
    print("          SLR(1) GRAMMAR CONFLICT CHECK")
    print("=" * 60)
    print("Default Grammar: ")
    print("  E -> E + T | T")
    print("  T -> T * F | F")
    print("  F -> ( E ) | id")
    print("-" * 60)
    use_default = input("Use default grammar? (Y/n): ").strip().lower()

    if use_default == 'n':
        n = int(input("Enter number of productions: "))
        raw_lines = [input().strip() for _ in range(n)]
    else:
        raw_lines = [
            "E->E+T|T",
            "T->T*F|F",
            "F->(E)|i"
        ]

    # Parse grammar dictionary for FIRST & FOLLOW
    prod_dict = {}
    productions = []
    non_terminals = []

    for line in raw_lines:
        line = line.strip().replace(" ", "")
        if "->" not in line:
            continue
        lhs, rhs = line.split("->", 1)
        if lhs not in non_terminals:
            non_terminals.append(lhs)
        if lhs not in prod_dict:
            prod_dict[lhs] = []
        for part in rhs.split("|"):
            prod_dict[lhs].append(part)
            productions.append((lhs, part))

    start = non_terminals[0]
    terminals = get_symbols(productions, non_terminals)

    first = compute_first(prod_dict, non_terminals, set(terminals))
    follow = compute_follow(prod_dict, start, non_terminals, set(terminals), first)

    print("\nFOLLOW SETS:")
    for nt in non_terminals:
        print(f"  FOLLOW({nt}) = {{ {', '.join(sorted(list(follow[nt])))} }}")

    # Augment grammar
    augmented_start = start + "'"
    productions.insert(0, (augmented_start, start))
    non_terminals.insert(0, augmented_start)
    all_symbols = [nt for nt in non_terminals if nt != augmented_start] + terminals

    # Build LR(0) states
    i0 = closure([(0, 0)], productions, non_terminals)
    states = [i0]
    queue = [0]
    while queue:
        curr = queue.pop(0)
        for sym in all_symbols:
            nxt = goto(states[curr], sym, productions, non_terminals)
            if nxt and nxt not in states:
                states.append(nxt)
                queue.append(len(states) - 1)

    print(f"\nConstructed {len(states)} Canonical LR(0) States.")

    # SLR(1) Conflict Check
    all_terminals = terminals + ['$']
    has_conflict = False

    for i, state in enumerate(states):
        # Shifts on terminals
        shifts = {}
        for sym in terminals:
            nxt = goto(state, sym, productions, non_terminals)
            if nxt:
                shifts[sym] = states.index(nxt)

        # Reductions
        action_map = {t: [] for t in all_terminals}
        for t, s_idx in shifts.items():
            action_map[t].append(f"Shift s{s_idx}")

        for prod_idx, dot in state:
            lhs, rhs = productions[prod_idx]
            if dot == len(rhs):
                if prod_idx == 0:
                    action_map['$'].append("Accept")
                else:
                    # In SLR(1), place reduce ONLY on FOLLOW(lhs)
                    for t in follow[lhs]:
                        action_map[t].append(f"Reduce {lhs}->{rhs}")

        # Check for multiple actions in any terminal slot
        for t, acts in action_map.items():
            if len(acts) > 1:
                has_conflict = True
                print(f"[!] Conflict in State I{i} on terminal '{t}': {acts}")

    print("\n" + "=" * 50)
    if not has_conflict:
        print("RESULT: Grammar is SLR(1) (No conflicts found).")
    else:
        print("RESULT: Grammar is NOT SLR(1) (SLR(1) conflicts detected).")
    print("=" * 50)

if __name__ == "__main__":
    main()

