"""
Practical: CLR(1) / Canonical LR(1) Conflict and Item Verification
Description:
    Computes LR(1) items with lookaheads, performs closure and goto operations,
    and checks if the grammar is CLR(1) (Canonical LR(1)) without conflicts.
"""

from first_follow import compute_first, first_of_string

def get_symbols(productions, non_terminals):
    terminals = set()
    for _, rhs in productions:
        for ch in rhs:
            if not ch.isupper() and ch not in ['#', '|']:
                terminals.add(ch)
    return sorted(list(terminals))

def clr1_closure(items, productions, non_terminals, terminals, first_table):
    # An item is a tuple: (prod_idx, dot, lookahead)
    closure_set = set(items)
    changed = True
    while changed:
        changed = False
        new_items = set()
        for prod_idx, dot, lookahead in closure_set:
            lhs, rhs = productions[prod_idx]
            if dot < len(rhs):
                B = rhs[dot]
                if B in non_terminals:
                    beta = rhs[dot + 1:]
                    beta_plus_lookahead = beta + lookahead
                    lookaheads = first_of_string(beta_plus_lookahead, first_table, set(terminals))
                    for i, (p_lhs, p_rhs) in enumerate(productions):
                        if p_lhs == B:
                            for b in lookaheads:
                                if b != '#':
                                    itm = (i, 0, b)
                                    if itm not in closure_set:
                                        new_items.add(itm)
        if new_items:
            closure_set.update(new_items)
            changed = True
    return tuple(sorted(list(closure_set)))

def clr1_goto(state_items, symbol, productions, non_terminals, terminals, first_table):
    moved = set()
    for prod_idx, dot, lookahead in state_items:
        lhs, rhs = productions[prod_idx]
        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((prod_idx, dot + 1, lookahead))
    if not moved:
        return ()
    return clr1_closure(moved, productions, non_terminals, terminals, first_table)

def format_clr_item(item, productions):
    prod_idx, dot, lookahead = item
    lhs, rhs = productions[prod_idx]
    dotted = rhs[:dot] + "." + rhs[dot:]
    return f"[{lhs} -> {dotted}, {lookahead}]"

def main():
    print("=" * 60)
    print("         CLR(1) GRAMMAR CONFLICT CHECK")
    print("=" * 60)
    print("Default Grammar: ")
    print("  S -> C C")
    print("  C -> c C | d")
    print("-" * 60)
    use_default = input("Use default grammar? (Y/n): ").strip().lower()

    if use_default == 'n':
        n = int(input("Enter number of productions: "))
        raw_lines = [input().strip() for _ in range(n)]
    else:
        raw_lines = [
            "S->CC",
            "C->cC|d"
        ]

    prod_dict = {}
    productions = []
    non_terminals = []

    for line in raw_lines:
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

    first_table = compute_first(prod_dict, non_terminals, set(terminals))

    augmented_start = start + "'"
    productions.insert(0, (augmented_start, start))
    non_terminals.insert(0, augmented_start)
    all_symbols = [nt for nt in non_terminals if nt != augmented_start] + terminals
    all_terminals = terminals + ['$']

    # Initial state I0
    i0 = clr1_closure([(0, 0, '$')], productions, non_terminals, terminals, first_table)
    states = [i0]
    queue = [0]
    while queue:
        curr = queue.pop(0)
        for sym in all_symbols:
            nxt = clr1_goto(states[curr], sym, productions, non_terminals, terminals, first_table)
            if nxt and nxt not in states:
                states.append(nxt)
                queue.append(len(states) - 1)

    print(f"\nGenerated {len(states)} Canonical LR(1) States:")
    for i, st in enumerate(states):
        print(f"\nState I{i}:")
        for itm in st:
            print(f"  {format_clr_item(itm, productions)}")

    # Check CLR(1) conflicts
    has_conflict = False
    for i, state in enumerate(states):
        actions = {t: [] for t in all_terminals}
        for sym in terminals:
            nxt = clr1_goto(state, sym, productions, non_terminals, terminals, first_table)
            if nxt:
                actions[sym].append(f"Shift s{states.index(nxt)}")

        for prod_idx, dot, lookahead in state:
            lhs, rhs = productions[prod_idx]
            if dot == len(rhs):
                if prod_idx == 0 and lookahead == '$':
                    actions['$'].append("Accept")
                else:
                    actions[lookahead].append(f"Reduce {lhs}->{rhs}")

        for t, acts in actions.items():
            if len(acts) > 1:
                has_conflict = True
                print(f"[!] Conflict in State I{i} on lookahead '{t}': {acts}")

    print("\n" + "=" * 50)
    if not has_conflict:
        print("RESULT: Grammar is CLR(1) (No conflicts detected).")
    else:
        print("RESULT: Grammar is NOT CLR(1) due to conflicts.")
    print("=" * 50)

if __name__ == "__main__":
    main()

