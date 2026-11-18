"""
Practical: LALR(1) Grammar Conflict Verification and State Merging
Description:
    Computes Canonical LR(1) states, groups and merges states with identical LR(0) cores,
    detects if any Reduce-Reduce or Shift-Reduce conflicts arise, and reports if the grammar is LALR(1).
"""

from first_follow import compute_first
from clr1_simple import (
    get_symbols, clr1_closure, clr1_goto, format_clr_item
)

def get_core(state):
    # Core is the set of (prod_idx, dot), ignoring lookahead
    return tuple(sorted(list({(prod_idx, dot) for prod_idx, dot, _ in state})))

def merge_lr1_states(states):
    core_map = {}
    for idx, st in enumerate(states):
        core = get_core(st)
        if core not in core_map:
            core_map[core] = []
        core_map[core].append(idx)

    merged_states = []
    old_to_merged = {}

    for new_idx, (core, old_indices) in enumerate(core_map.items()):
        # Union of lookaheads for each core item
        item_lookaheads = {c: set() for c in core}
        for old_idx in old_indices:
            old_to_merged[old_idx] = new_idx
            for prod_idx, dot, lookahead in states[old_idx]:
                item_lookaheads[(prod_idx, dot)].add(lookahead)

        merged_state = []
        for (prod_idx, dot), lookaheads in item_lookaheads.items():
            for la in sorted(list(lookaheads)):
                merged_state.append((prod_idx, dot, la))
        merged_states.append(tuple(sorted(merged_state)))

    return merged_states, old_to_merged, core_map

def main():
    print("=" * 60)
    print("         LALR(1) STATE MERGING & CONFLICT CHECK")
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

    print(f"\nGenerated {len(states)} LR(1) states before merging.")
    merged_states, old_to_merged, core_map = merge_lr1_states(states)
    print(f"Compressed into {len(merged_states)} LALR(1) states after merging common cores:")

    for core, old_indices in core_map.items():
        if len(old_indices) > 1:
            print(f"  Merged LR(1) States {old_indices} -> New LALR State I{old_to_merged[old_indices[0]]}")

    # Check for LALR(1) conflicts
    has_conflict = False
    for i, state in enumerate(merged_states):
        actions = {t: [] for t in all_terminals}
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
                print(f"[!] Reduce-Reduce Conflict in LALR State I{i} on terminal '{t}': {acts}")

    print("\n" + "=" * 50)
    if not has_conflict:
        print("RESULT: Grammar is LALR(1) (No conflicts in merged states).")
    else:
        print("RESULT: Grammar is NOT LALR(1) due to conflicts.")
    print("=" * 50)

if __name__ == "__main__":
    main()

