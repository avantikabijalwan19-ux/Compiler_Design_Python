"""
Practical: LR(0) Input String Verification and Parsing Simulator
Description:
    Interactively verifies multiple input strings against the LR(0) parser,
    showing step-by-step stack moves, actions, and accept/reject outcomes.
"""

from lr0_parser import (
    closure, goto, get_symbols, build_lr0_table, parse_input_lr0
)

def main():
    print("=" * 65)
    print("       LR(0) STRING VALIDATION & PARSING SIMULATOR")
    print("=" * 65)
    print("Default Grammar: ")
    print("  S -> A A")
    print("  A -> a A | b")
    print("-" * 65)
    
    use_default = input("Use default grammar? (Y/n): ").strip().lower()
    if use_default == 'n':
        n = int(input("Enter number of productions: "))
        raw_lines = [input().strip() for _ in range(n)]
    else:
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

    if not is_lr0:
        print("\n[!] WARNING: Grammar contains LR(0) conflicts. Deterministic LR(0) parsing may fail.")

    test_samples = ["aabb", "ab", "b", "aa", "aab"]
    print(f"\nSample test strings for this grammar: {', '.join(test_samples)}")

    while True:
        test_str = input("\nEnter string to validate (or press Enter to finish): ").strip()
        if not test_str:
            break
        result = parse_input_lr0(test_str, action_table, goto_table, productions)
        if result:
            print(f">>> Result: '{test_str}' is a VALID sentence (ACCEPTED).")
        else:
            print(f">>> Result: '{test_str}' is an INVALID sentence (REJECTED).")

if __name__ == "__main__":
    main()

