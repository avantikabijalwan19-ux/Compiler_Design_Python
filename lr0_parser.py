"""
Practical: LR(0) Parsing Table Construction and String Validation
Description:
    Builds the canonical LR(0) collection of items, generates the ACTION and GOTO tables,
    and tests input strings using the bottom-up shift-reduce parsing algorithm.
"""

def get_symbols(productions, non_terminals):
    terminals = set()
    for _, rhs in productions:
        for ch in rhs:
            if not ch.isupper() and ch not in ['#', '|']:
                terminals.add(ch)
    return sorted(list(terminals))

def closure(items, productions, non_terminals):
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

def build_lr0_table(states, productions, terminals, non_terminals, augmented_start):
    action_table = {}
    goto_table = {}
    all_terminals = terminals + ['$']
    var_symbols = [nt for nt in non_terminals if nt != augmented_start]

    for i in range(len(states)):
        action_table[i] = {t: [] for t in all_terminals}
        goto_table[i] = {v: None for v in var_symbols}

    # Transitions
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

        # Reductions
        for prod_idx, dot in state:
            lhs, rhs = productions[prod_idx]
            if dot == len(rhs):
                if prod_idx == 0:  # S' -> S.
                    action_table[i]['$'].append("acc")
                else:
                    for t in all_terminals:
                        action_table[i][t].append(f"r{prod_idx}")

    is_lr0 = True
    for i in range(len(states)):
        for t in all_terminals:
            if len(action_table[i][t]) > 1:
                is_lr0 = False

    return action_table, goto_table, all_terminals, var_symbols, is_lr0

def parse_input_lr0(input_str, action_table, goto_table, productions):
    tokens = list(input_str)
    if not tokens or tokens[-1] != '$':
        tokens.append('$')

    state_stack = [0]
    symbol_stack = ['$']
    ip = 0

    print("\n" + "=" * 80)
    print(f"{'STATE STACK':<20} {'SYMBOL STACK':<20} {'INPUT':<20} {'ACTION':<20}")
    print("=" * 80)

    while True:
        s = state_stack[-1]
        a = tokens[ip]
        actions = action_table[s].get(a, [])

        st_str = " ".join(map(str, state_stack))
        sym_str = "".join(symbol_stack)
        in_str = "".join(tokens[ip:])

        if not actions:
            print(f"{st_str:<20} {sym_str:<20} {in_str:<20} {'ERROR (Reject)':<20}")
            return False

        act = actions[0]

        if act.startswith('s'):
            next_state = int(act[1:])
            print(f"{st_str:<20} {sym_str:<20} {in_str:<20} {f'Shift to state {next_state}':<20}")
            symbol_stack.append(a)
            state_stack.append(next_state)
            ip += 1
        elif act.startswith('r'):
            prod_idx = int(act[1:])
            lhs, rhs = productions[prod_idx]
            pop_len = len(rhs)
            for _ in range(pop_len):
                state_stack.pop()
                symbol_stack.pop()
            top_state = state_stack[-1]
            goto_state = goto_table[top_state][lhs]
            state_stack.append(goto_state)
            symbol_stack.append(lhs)
            print(f"{st_str:<20} {sym_str:<20} {in_str:<20} {f'Reduce by {lhs}->{rhs}':<20}")
        elif act == 'acc':
            print(f"{st_str:<20} {sym_str:<20} {in_str:<20} {'ACCEPT (Success)':<20}")
            return True
        else:
            print(f"{st_str:<20} {sym_str:<20} {in_str:<20} {'CONFLICT/ERROR':<20}")
            return False

def main():
    print("=" * 60)
    print("         LR(0) PARSER TABLE AND STRING TRACE")
    print("=" * 60)
    use_default = input("Use default grammar? (Y/n): ").strip().lower()

    if use_default == 'n':
        n = int(input("Enter number of productions: "))
        raw_lines = [input().strip() for _ in range(n)]
    else:
        # Standard LR(0) grammar
        raw_lines = [
            "S->AA",
            "A->aA",
            "A->b"
        ]

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

    start = non_terminals[0]
    augmented_start = start + "'"
    productions.insert(0, (augmented_start, start))
    non_terminals.insert(0, augmented_start)

    terminals = get_symbols(productions, non_terminals)
    all_symbols = [nt for nt in non_terminals if nt != augmented_start] + terminals

    # Build canonical states
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

    action_table, goto_table, all_terminals, var_symbols, is_lr0 = build_lr0_table(
        states, productions, terminals, non_terminals, augmented_start
    )

    print("\nNumbered Productions:")
    for idx, (lhs, rhs) in enumerate(productions):
        print(f"  ({idx}) {lhs} -> {rhs}")

    print("\n--- LR(0) PARSING TABLE ---")
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
    print(f"Grammar is {'LR(0)' if is_lr0 else 'NOT LR(0) (contains conflicts)'}")
    print("=" * 50)

    inp = input("\nEnter input string (default: 'ab'): ").strip()
    if not inp:
        inp = "ab"

    parse_input_lr0(inp, action_table, goto_table, productions)

if __name__ == "__main__":
    main()

