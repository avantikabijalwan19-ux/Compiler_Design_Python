"""
Practical: LALR(1) Parsing Table Construction and String Parsing
Description:
    Constructs the LALR(1) Parsing Table by merging LR(1) states with identical cores,
    displays the compact parsing table, and parses candidate input sentences.
"""

from first_follow import compute_first
from clr1_simple import (
    get_symbols, clr1_closure, clr1_goto
)
from lalr1_simple import merge_lr1_states
from lr0_parser import parse_input_lr0

def build_lalr1_table(lr1_states, productions, terminals, non_terminals, augmented_start, first_table):
    all_terminals = terminals + ['$']
    var_symbols = [nt for nt in non_terminals if nt != augmented_start]

    merged_states, old_to_merged, _ = merge_lr1_states(lr1_states)
    num_merged = len(merged_states)

    action_table = {i: {t: [] for t in all_terminals} for i in range(num_merged)}
    goto_table = {i: {v: None for v in var_symbols} for i in range(num_merged)}

    # Transitions from merged states
    for i, state in enumerate(merged_states):
        # Shifts on terminals
        for sym in terminals:
            nxt = clr1_goto(state, sym, productions, non_terminals, terminals, first_table)
            if nxt:
                # Find matching core in merged states
                nxt_core = tuple(sorted(list({(p, d) for p, d, _ in nxt})))
                for m_idx, m_st in enumerate(merged_states):
                    m_core = tuple(sorted(list({(p, d) for p, d, _ in m_st})))
                    if m_core == nxt_core:
                        action_table[i][sym].append(f"s{m_idx}")
                        break

        # Gotos on non-terminals
        for sym in var_symbols:
            nxt = clr1_goto(state, sym, productions, non_terminals, terminals, first_table)
            if nxt:
                nxt_core = tuple(sorted(list({(p, d) for p, d, _ in nxt})))
                for m_idx, m_st in enumerate(merged_states):
                    m_core = tuple(sorted(list({(p, d) for p, d, _ in m_st})))
                    if m_core == nxt_core:
                        goto_table[i][sym] = m_idx
                        break

        # Reductions
        for prod_idx, dot, lookahead in state:
            lhs, rhs = productions[prod_idx]
            if dot == len(rhs):
                if prod_idx == 0 and lookahead == '$':
                    if "acc" not in action_table[i]['$']:
                        action_table[i]['$'].append("acc")
                else:
                    red_str = f"r{prod_idx}"
                    if red_str not in action_table[i][lookahead]:
                        action_table[i][lookahead].append(red_str)

    is_lalr1 = True
    for i in range(num_merged):
        for t in all_terminals:
            # Deduplicate entries if any
            unique_acts = list(dict.fromkeys(action_table[i][t]))
            action_table[i][t] = unique_acts
            if len(unique_acts) > 1:
                is_lalr1 = False

    return action_table, goto_table, all_terminals, var_symbols, is_lalr1, merged_states

def main():
    print("=" * 65)
    print("       LALR(1) PARSING TABLE GENERATOR AND PARSER")
    print("=" * 65)
    use_default = input("Use default grammar (S->CC, C->cC|d)? (Y/n): ").strip().lower()

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

    action_table, goto_table, all_terminals, var_symbols, is_lalr1, merged_states = build_lalr1_table(
        states, productions, terminals, non_terminals, augmented_start, first_table
    )

    print("\nNumbered Productions:")
    for idx, (lhs, rhs) in enumerate(productions):
        print(f"  ({idx}) {lhs} -> {rhs}")

    print("\n--- LALR(1) PARSING TABLE ---")
    hdr = f"{'State':<6}" + "".join([f"{t:<8}" for t in all_terminals]) + "|" + "".join([f"{v:<8}" for v in var_symbols])
    print(hdr)
    print("-" * len(hdr))
    for i in range(len(merged_states)):
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
    print(f"Grammar is {'LALR(1)' if is_lalr1 else 'NOT LALR(1) (Contains conflicts)'}")
    print("=" * 50)

    test_input = input("\nEnter input string (default: 'cdd'): ").strip()
    if not test_input:
        test_input = "cdd"

    parse_input_lr0(test_input, action_table, goto_table, productions)

if __name__ == "__main__":
    main()

