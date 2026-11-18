"""
Practical: LALR(1) String Check and Interactive Verification
Description:
    Runs interactive string testing against the generated LALR(1) table,
    logging shift/reduce decisions and evaluating sentence acceptance.
"""

from first_follow import compute_first
from clr1_simple import get_symbols, clr1_closure, clr1_goto
from lalr1_parser import build_lalr1_table
from lr0_parser import parse_input_lr0

def main():
    print("=" * 65)
    print("       LALR(1) INTERACTIVE STRING VERIFICATION")
    print("=" * 65)
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

    print(f"Grammar loaded successfully. LALR(1) Status: {'Compatible' if is_lalr1 else 'Has Conflicts'}")
    test_samples = ["cdd", "dd", "ccd", "cdcd", "d"]
    print(f"Sample test strings: {', '.join(test_samples)}")

    while True:
        s = input("\nEnter test string (or press Enter to exit): ").strip()
        if not s:
            break
        res = parse_input_lr0(s, action_table, goto_table, productions)
        if res:
            print(f">>> Result: '{s}' is a VALID sentence (ACCEPTED).")
        else:
            print(f">>> Result: '{s}' is an INVALID sentence (REJECTED).")

if __name__ == "__main__":
    main()

