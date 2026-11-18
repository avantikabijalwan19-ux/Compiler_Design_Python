"""
Practical: LL(1) Predictive Parser Construction and String Validation
Description:
    Computes FIRST & FOLLOW sets, constructs LL(1) Parsing Table,
    detects conflicts to verify if the grammar is LL(1),
    and validates an input string step-by-step using an explicit parsing stack.
"""

def compute_first(productions, non_terminals, terminals):
    first = {nt: set() for nt in non_terminals}

    def first_of_symbol(sym):
        if sym in terminals or sym == '#':
            return {sym}
        return first[sym]

    changed = True
    while changed:
        changed = False
        for lhs, rhs_list in productions.items():
            for rhs in rhs_list:
                before = len(first[lhs])
                if rhs == '#' or rhs == '':
                    first[lhs].add('#')
                else:
                    all_eps = True
                    for sym in rhs:
                        sym_first = first_of_symbol(sym)
                        first[lhs].update(sym_first - {'#'})
                        if '#' not in sym_first:
                            all_eps = False
                            break
                    if all_eps:
                        first[lhs].add('#')
                if len(first[lhs]) > before:
                    changed = True
    return first

def first_of_string(string, first, terminals):
    if not string or string == '#':
        return {'#'}
    res = set()
    all_eps = True
    for sym in string:
        if sym in terminals or sym == '#':
            res.add(sym)
            all_eps = False
            break
        sym_first = first.get(sym, set())
        res.update(sym_first - {'#'})
        if '#' not in sym_first:
            all_eps = False
            break
    if all_eps:
        res.add('#')
    return res

def compute_follow(productions, start_symbol, non_terminals, terminals, first):
    follow = {nt: set() for nt in non_terminals}
    follow[start_symbol].add('$')

    changed = True
    while changed:
        changed = False
        for lhs, rhs_list in productions.items():
            for rhs in rhs_list:
                if rhs == '#':
                    continue
                for i, sym in enumerate(rhs):
                    if sym in non_terminals:
                        before = len(follow[sym])
                        beta = rhs[i + 1:]
                        if beta:
                            first_beta = first_of_string(beta, first, terminals)
                            follow[sym].update(first_beta - {'#'})
                            if '#' in first_beta:
                                follow[sym].update(follow[lhs])
                        else:
                            follow[sym].update(follow[lhs])
                        if len(follow[sym]) > before:
                            changed = True
    return follow

def build_ll1_table(productions, non_terminals, terminals, first, follow):
    all_terminals = sorted(list(terminals - {'#'})) + ['$']
    table = {nt: {t: [] for t in all_terminals} for nt in non_terminals}
    is_ll1 = True

    for lhs, rhs_list in productions.items():
        for rhs in rhs_list:
            first_alpha = first_of_string(rhs, first, terminals)
            for terminal in first_alpha - {'#'}:
                table[lhs][terminal].append(rhs)
            if '#' in first_alpha:
                for terminal in follow[lhs]:
                    table[lhs][terminal].append(rhs)

    # Check conflicts
    for nt in non_terminals:
        for t in all_terminals:
            if len(table[nt][t]) > 1:
                is_ll1 = False

    return table, all_terminals, is_ll1

def parse_string(input_str, table, start_symbol, terminals):
    stack = ['$', start_symbol]
    ip = 0
    buffer = list(input_str)
    if not buffer or buffer[-1] != '$':
        buffer.append('$')

    print("\n" + "=" * 70)
    print(f"{'STACK':<25} {'INPUT':<20} {'ACTION':<25}")
    print("=" * 70)

    while len(stack) > 0:
        top = stack[-1]
        current_input = buffer[ip] if ip < len(buffer) else '$'
        stack_str = "".join(stack)
        input_str_remaining = "".join(buffer[ip:])

        if top == current_input:
            if top == '$':
                print(f"{stack_str:<25} {input_str_remaining:<20} {'ACCEPT (String Valid)':<25}")
                return True
            else:
                stack.pop()
                ip += 1
                print(f"{stack_str:<25} {input_str_remaining:<20} {f'Matched terminal {top}':<25}")
        elif top in terminals or top == '$':
            print(f"{stack_str:<25} {input_str_remaining:<20} {f'Error: Expected {top}, got {current_input}':<25}")
            return False
        else:
            if current_input not in table[top] or not table[top][current_input]:
                print(f"{stack_str:<25} {input_str_remaining:<20} {f'Error: No entry for [{top}, {current_input}]':<25}")
                return False
            production = table[top][current_input][0]
            stack.pop()
            if production != '#':
                for sym in reversed(production):
                    stack.append(sym)
            print(f"{stack_str:<25} {input_str_remaining:<20} {f'Output {top} -> {production}':<25}")

    return False

def main():
    print("=" * 70)
    print("       LL(1) PARSER GENERATOR AND STRING VALIDATION")
    print("=" * 70)
    use_default = input("Use default arithmetic grammar? (Y/n): ").strip().lower()

    if use_default == 'n':
        n = int(input("Enter number of productions: "))
        lines = []
        for _ in range(n):
            lines.append(input().strip())
    else:
        # Standard unambiguous LL(1) grammar:
        # E -> T X
        # X -> + T X | #
        # T -> F Y
        # Y -> * F Y | #
        # F -> ( E ) | i
        lines = [
            "E->TX",
            "X->+TX|#",
            "T->FY",
            "Y->*FY|#",
            "F->(E)|i"
        ]

    productions = {}
    non_terminals = []
    terminals = set()

    for line in lines:
        line = line.strip().replace(" ", "")
        if not line or "->" not in line:
            continue
        lhs, rhs_part = line.split("->", 1)
        if lhs not in non_terminals:
            non_terminals.append(lhs)
        if lhs not in productions:
            productions[lhs] = []
        for rhs in rhs_part.split("|"):
            productions[lhs].append(rhs)
            for ch in rhs:
                if not ch.isupper() and ch not in ['#', '|']:
                    terminals.add(ch)

    start_symbol = non_terminals[0]
    first = compute_first(productions, non_terminals, terminals)
    follow = compute_follow(productions, start_symbol, non_terminals, terminals, first)
    table, all_terminals, is_ll1 = build_ll1_table(productions, non_terminals, terminals, first, follow)

    print("\n--- LL(1) PARSING TABLE ---")
    header = f"{'Non-Term':<10}" + "".join([f"{t:<12}" for t in all_terminals])
    print(header)
    print("-" * len(header))
    for nt in non_terminals:
        row = f"{nt:<10}"
        for t in all_terminals:
            entries = table[nt][t]
            if entries:
                cell = f"{nt}->{','.join(entries)}"
            else:
                cell = "---"
            row += f"{cell:<12}"
        print(row)

    print("\n" + "=" * 40)
    if is_ll1:
        print("Grammar is LL(1): No conflicts found.")
    else:
        print("Grammar is NOT LL(1): Multiple entries found in table cell(s).")
    print("=" * 40)

    test_input = input("\nEnter input string to test (default: 'i+i*i'): ").strip()
    if not test_input:
        test_input = "i+i*i"

    res = parse_string(test_input, table, start_symbol, terminals)
    if res:
        print("\n>>> String ACCEPTED by LL(1) Parser! <<<")
    else:
        print("\n>>> String REJECTED by LL(1) Parser! <<<")

if __name__ == "__main__":
    main()

