"""
Practical: SLR(1) Parsing Table Construction and String Parsing
Description:
    Builds the SLR(1) Parsing Table using LR(0) canonical items and FOLLOW sets,
    validates the grammar for SLR(1) compliance, and performs stack-based parsing.
"""

from first_follow import compute_first, compute_follow
from lr0_parser import closure, goto, get_symbols, parse_input_lr0

def build_slr1_table(states, productions, terminals, non_terminals, follow, augmented_start):
    all_terminals = terminals + ['$']
    var_symbols = [nt for nt in non_terminals if nt != augmented_start]

    action_table = {i: {t: [] for t in all_terminals} for i in range(len(states))}
    goto_table = {i: {v: None for v in var_symbols} for i in range(len(states))}

    # Shifts and Gotos
    for i, state in enumerate(states):
        for sym in terminals:
            nxt = goto(state, sym, productions, non_terminals)
            if nxt in states:
                nxt_idx = states.index(nxt)
                action_table[i][sym].append(f"s{nxt_idx}")

        for sym in var_symbols:
            nxt = goto(state, sym, productions, non_terminals)
            if nxt in states:
                goto_table[i][sym] = states.index(nxt)

        # Reductions: ONLY in FOLLOW(lhs)
        for prod_idx, dot in state:
            lhs, rhs = productions[prod_idx]
            if dot == len(rhs):
                if prod_idx == 0:  # S' -> S.
                    action_table[i]['$'].append("acc")
                else:
                    for t in follow[lhs]:
                        action_table[i][t].append(f"r{prod_idx}")

    is_slr1 = True
    for i in range(len(states)):
        for t in all_terminals:
            if len(action_table[i][t]) > 1:
                is_slr1 = False

    return action_table, goto_table, all_terminals, var_symbols, is_slr1

def main():
    print("=" * 65)
    print("       SLR(1) PARSING TABLE GENERATOR AND TESTER")
    print("=" * 65)
    use_default = input("Use default arithmetic grammar? (Y/n): ").strip().lower()

    if use_default == 'n':
        n = int(input("Enter number of productions: "))
        raw_lines = [input().strip() for _ in range(n)]
    else:
        # Classic SLR(1) grammar
        raw_lines = [
            "E->E+T|T",
            "T->T*F|F",
            "F->(E)|i"
        ]

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

    augmented_start = start + "'"
    productions.insert(0, (augmented_start, start))
    non_terminals.insert(0, augmented_start)
    all_symbols = [nt for nt in non_terminals if nt != augmented_start] + terminals

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

    action_table, goto_table, all_terminals, var_symbols, is_slr1 = build_slr1_table(
        states, productions, terminals, non_terminals, follow, augmented_start
    )

    print("\nNumbered Productions:")
    for idx, (lhs, rhs) in enumerate(productions):
        print(f"  ({idx}) {lhs} -> {rhs}")

    print("\n--- SLR(1) PARSING TABLE ---")
    hdr = f"{'State':<6}" + "".join([f"{t:<8}" for t in all_terminals]) + "|" + "".join([f"{v:<8}" for v in var_symbols])
    print(hdr)
    print("-" * len(hdr))
    for i in range(len(states)):
        row = f"{i:<6}"
        for t in all_terminals:
            acts = action_table[i][t]
            cell = "/".join(acts) if acts else "."
            row += f"{cell:<8}"
        row += "|"
        for v in var_symbols:
            gt = goto_table[i][v]
            cell = str(gt) if gt is not None else "."
            row += f"{cell:<8}"
        print(row)

    print("\n" + "=" * 50)
    print(f"Grammar is {'SLR(1)' if is_slr1 else 'NOT SLR(1) (Conflicts exist)'}")
    print("=" * 50)

    test_input = input("\nEnter input string to parse (default: 'i+i*i'): ").strip()
    if not test_input:
        test_input = "i+i*i"

    parse_input_lr0(test_input, action_table, goto_table, productions)

if __name__ == "__main__":
    main()

