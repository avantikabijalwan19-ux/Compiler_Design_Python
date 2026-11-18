"""
Practical: Computation of FIRST and FOLLOW sets for Context-Free Grammars (CFG)
Description:
    Computes the FIRST and FOLLOW sets for all non-terminals in a CFG.
    Epsilon is represented by '#' or 'e'.
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
                before_count = len(first[lhs])
                if rhs == '#' or rhs == '':
                    first[lhs].add('#')
                else:
                    all_have_epsilon = True
                    for symbol in rhs:
                        sym_first = first_of_symbol(symbol)
                        first[lhs].update(sym_first - {'#'})
                        if '#' not in sym_first:
                            all_have_epsilon = False
                            break
                    if all_have_epsilon:
                        first[lhs].add('#')
                if len(first[lhs]) > before_count:
                    changed = True

    return first

def compute_first_of_string(string, first, terminals):
    if not string or string == '#':
        return {'#'}
    result = set()
    all_epsilon = True
    term_set = set(terminals) | {'$'}
    for sym in string:
        if sym in term_set or not sym.isupper() or sym == '#':
            result.add(sym)
            all_epsilon = False
            break
        sym_first = first.get(sym, set())
        result.update(sym_first - {'#'})
        if '#' not in sym_first:
            all_epsilon = False
            break
    if all_epsilon:
        result.add('#')
    return result

# Alias for convenience
first_of_string = compute_first_of_string

def compute_follow(productions, start_symbol, non_terminals, terminals, first):
    follow = {nt: set() for nt in non_terminals}
    follow[start_symbol].add('$')  # End marker in start symbol's FOLLOW

    changed = True
    while changed:
        changed = False
        for lhs, rhs_list in productions.items():
            for rhs in rhs_list:
                if rhs == '#':
                    continue
                for i, sym in enumerate(rhs):
                    if sym in non_terminals:
                        before_count = len(follow[sym])
                        beta = rhs[i + 1:]
                        if beta:
                            first_beta = compute_first_of_string(beta, first, terminals)
                            follow[sym].update(first_beta - {'#'})
                            if '#' in first_beta:
                                follow[sym].update(follow[lhs])
                        else:
                            follow[sym].update(follow[lhs])
                        if len(follow[sym]) > before_count:
                            changed = True

    return follow

def parse_grammar(lines):
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
                if not ch.isupper() and ch not in ['#', '|', 'ε']:
                    terminals.add(ch)

    return productions, non_terminals, sorted(list(terminals))

def main():
    print("=" * 60)
    print("       FIRST AND FOLLOW SET COMPUTATION FOR CFG")
    print("=" * 60)
    print("Default Grammar: ")
    print("  E -> T E'")
    print("  E' -> + T E' | #")
    print("  T -> F T'")
    print("  T' -> * F T' | #")
    print("  F -> ( E ) | id")
    print("-" * 60)
    use_default = input("Use default grammar? (Y/n): ").strip().lower()

    if use_default == 'n':
        n = int(input("Enter number of productions: "))
        lines = []
        print("Enter productions (e.g. E->TX or E->+TE'|# where # is epsilon):")
        for _ in range(n):
            lines.append(input().strip())
    else:
        # Simplified standard non-terminal single-letter representation
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

    productions, non_terminals, terminals = parse_grammar(lines)
    start_symbol = non_terminals[0]

    print("\nProductions:")
    for lhs, rhs_list in productions.items():
        print(f"  {lhs} -> {' | '.join(rhs_list)}")

    first = compute_first(productions, non_terminals, terminals)
    follow = compute_follow(productions, start_symbol, non_terminals, terminals, first)

    print("\n" + "=" * 30 + " FIRST SETS " + "=" * 30)
    for nt in non_terminals:
        items = sorted(list(first[nt]))
        print(f"FIRST({nt})  = {{ {', '.join(items)} }}")

    print("\n" + "=" * 30 + " FOLLOW SETS " + "=" * 30)
    for nt in non_terminals:
        items = sorted(list(follow[nt]))
        print(f"FOLLOW({nt}) = {{ {', '.join(items)} }}")
    print("=" * 72)

if __name__ == "__main__":
    main()
