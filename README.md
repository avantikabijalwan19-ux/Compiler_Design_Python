# Compiler Design Lab Practicals (Python Implementation)

A comprehensive, modular, and educational implementation of all fundamental **Compiler Design Syntax Analysis (Parsing)** practicals written in Python. This repository translates traditional C-based compiler practicals into clear, idiomatic, and readable Python code with step-by-step visualizations.

---

## 📚 Table of Contents
1. [Overview](#overview)
2. [Hierarchy of Parsers](#hierarchy-of-parsers)
3. [Practicals Index](#practicals-index)
4. [Detailed Practical Descriptions](#detailed-practical-descriptions)
   - [Practical 1: FIRST and FOLLOW Set Computation](#practical-1-first-and-follow-set-computation)
   - [Practical 2: LL(1) Predictive Parser](#practical-2-ll1-predictive-parser)
   - [Practical 3–5: LR(0) Parser Suite](#practical-35-lr0-parser-suite)
   - [Practical 6–8: SLR(1) Parser Suite](#practical-68-slr1-parser-suite)
   - [Practical 9–11: CLR(1) Parser Suite](#practical-911-clr1-parser-suite)
   - [Practical 12–14: LALR(1) Parser Suite](#practical-1214-lalr1-parser-suite)
5. [Grammar Format & Conventions](#grammar-format--conventions)
6. [How to Run](#how-to-run)
7. [Dependencies & Requirements](#dependencies--requirements)

---

## 🔍 Overview
Syntax Analysis (Parsing) is the second phase of a compiler. It checks whether a sequence of tokens adheres to the syntactic specification defined by a Context-Free Grammar (CFG).

This suite covers:
- **Top-Down Parsing:** Recursive First/Follow computation and Non-recursive Predictive LL(1) parsing.
- **Bottom-Up Parsing (Shift-Reduce):**
  - **LR(0):** Canonical collection of items without lookahead.
  - **SLR(1):** Simple LR using $FOLLOW$ sets to reduce conflicts.
  - **CLR(1):** Canonical LR with lookaheads $[A \to \alpha \cdot \beta, a]$.
  - **LALR(1):** Look-Ahead LR merging identical core states for space efficiency.

---

## 📊 Hierarchy of Parsers

```
                ┌─────────────────────────────┐
                │        LR(1) / CLR(1)       │ (Most Powerful, Largest States)
                └──────────────┬──────────────┘
                               │ Merges core states
                ┌──────────────▼──────────────┐
                │           LALR(1)           │ (Yacc / Bison / Modern Compilers)
                └──────────────┬──────────────┘
                               │ Restricts reduction to FOLLOW(A)
                ┌──────────────▼──────────────┐
                │           SLR(1)            │
                └──────────────┬──────────────┘
                               │ No lookahead on reduction
                ┌──────────────▼──────────────┐
                │            LR(0)            │ (Weakest Bottom-Up Parser)
                └─────────────────────────────┘
```

---

## 🗂 Practicals Index

| File Name | Category | Purpose |
|---|---|---|
| `first_follow.py` | Top-Down Analysis | Computes FIRST and FOLLOW sets for non-terminals in a CFG. |
| `ll1_parser.py` | Top-Down Parser | Constructs LL(1) table, checks conflicts, and traces string derivation. |
| `lr0_simple.py` | Bottom-Up Parser | Constructs LR(0) item sets and detects Shift-Reduce / Reduce-Reduce conflicts. |
| `lr0_parser.py` | Bottom-Up Parser | Constructs ACTION and GOTO tables for LR(0) and verifies input strings. |
| `lr0_input_string_check.py` | Parser Simulation | Interactive tester for evaluating candidate tokens with LR(0) stack trace. |
| `slr1_simple.py` | Bottom-Up Parser | Validates SLR(1) compatibility by restricting reductions to $FOLLOW(A)$. |
| `slr1_parser.py` | Bottom-Up Parser | Builds full SLR(1) parsing table with ACTION & GOTO matrices. |
| `slr1_input_string_check.py` | Parser Simulation | Interactive multi-test harness for validating sentences using SLR(1). |
| `clr1_simple.py` | Canonical LR | Computes LR(1) items with lookahead $[A \to \alpha \cdot \beta, a]$ and checks conflicts. |
| `clr1_parser.py` | Canonical LR | Builds complete CLR(1) table, displaying state items and transitions. |
| `clr1_input_string_check.py` | Parser Simulation | Validates sentences with CLR(1) table using stack-based shift-reduce trace. |
| `lalr1_simple.py` | Compact LR | Merges CLR(1) states with identical LR(0) cores and checks for conflicts. |
| `lalr1_parser.py` | Compact LR | Generates compact LALR(1) table with state indices and transition mapping. |
| `lalr1_input_string_check.py` | Parser Simulation | Interactive testing harness for LALR(1) grammars. |

---

## 📖 Detailed Practical Descriptions

### Practical 1: FIRST and FOLLOW Set Computation
- **File:** `first_follow.py`
- **Algorithm:**
  - $FIRST(\alpha)$: Set of terminals that begin strings derived from $\alpha$.
  - $FOLLOW(A)$: Set of terminals that can appear immediately to the right of non-terminal $A$.
- **Sample Run:**
  ```bash
  python first_follow.py
  ```
- **Output:**
  ```text
  FIRST(E)  = { (, i }
  FIRST(X)  = { #, + }
  FOLLOW(E) = { $, ) }
  FOLLOW(T) = { $, ), + }
  ```

---

### Practical 2: LL(1) Predictive Parser
- **File:** `ll1_parser.py`
- **Concept:** Constructs table $M[A, a]$ where for production $A \to \alpha$:
  - Add $A \to \alpha$ to $M[A, a]$ for all $a \in FIRST(\alpha)$.
  - If $\epsilon \in FIRST(\alpha)$, add $A \to \alpha$ to $M[A, b]$ for all $b \in FOLLOW(A)$.
- **Parsing:** Uses an explicit stack initialized to `['$', 'S']`. Matches terminals or expands non-terminals.

---

### Practical 3–5: LR(0) Parser Suite
- **Files:** `lr0_simple.py`, `lr0_parser.py`, `lr0_input_string_check.py`
- **Concept:**
  - Augments grammar with $S' \to S$.
  - Generates items $A \to \alpha \cdot \beta$ using `CLOSURE` and `GOTO`.
  - Places reduction $r_i$ across **all terminals** in $ACTION[i, \cdot]$.
  - Identifies **Shift-Reduce (SR)** and **Reduce-Reduce (RR)** conflicts.

---

### Practical 6–8: SLR(1) Parser Suite
- **Files:** `slr1_simple.py`, `slr1_parser.py`, `slr1_input_string_check.py`
- **Concept:**
  - Refines LR(0) by placing reduction $A \to \alpha$ **only in $FOLLOW(A)$**.
  - Eliminates many spurious Shift-Reduce conflicts present in pure LR(0).

---

### Practical 9–11: CLR(1) Parser Suite
- **Files:** `clr1_simple.py`, `clr1_parser.py`, `clr1_input_string_check.py`
- **Concept:**
  - Carries a lookahead terminal with every item: $[A \to \alpha \cdot \beta, a]$.
  - Reduces $A \to \alpha$ on terminal $a$ only when $a$ equals the lookahead.
  - Prevents conflicts by splitting states that have different context lookaheads.

---

### Practical 12–14: LALR(1) Parser Suite
- **Files:** `lalr1_simple.py`, `lalr1_parser.py`, `lalr1_input_string_check.py`
- **Concept:**
  - Detects states in the CLR(1) automaton having identical cores $(A \to \alpha \cdot \beta)$.
  - Merges these states by taking the union of their lookaheads.
  - Produces an automaton with the exact same number of states as LR(0), but with the lookahead precision of LR(1).

---

## 📝 Grammar Format & Conventions

- **Non-Terminals:** Uppercase letters (`E`, `T`, `F`, `S`, `C`, `A`, `B`).
- **Terminals:** Lowercase letters or symbols (`+`, `*`, `(`, `)`, `i`, `a`, `b`, `c`, `d`).
- **Epsilon (Null):** Represented by `#` or `ε`.
- **End of Input Marker:** Represented by `$`.
- **Production Syntax:**
  ```text
  E->TX
  X->+TX|#
  T->FY
  Y->*FY|#
  F->(E)|i
  ```
- *Every script provides interactive default grammars if you press Enter, while allowing custom grammars.*

---

## 🚀 How to Run

You can execute any practical directly with standard Python 3:

```bash
# 1. Run First and Follow computation
python first_follow.py

# 2. Run LL(1) Parser
python ll1_parser.py

# 3. Check if grammar is LR(0)
python lr0_simple.py

# 4. Generate LR(0) table & parse
python lr0_parser.py

# 5. Check SLR(1) grammar
python slr1_simple.py

# 6. Generate SLR(1) table & parse
python slr1_parser.py

# 7. Generate CLR(1) table & parse
python clr1_parser.py

# 8. Generate LALR(1) table & parse
python lalr1_parser.py
```

---

## ⚙️ Dependencies & Requirements
- **Python Version:** Python 3.8+ (tested on Python 3.10)
- **External Libraries:** **None!** (Pure standard library: `sys`, `collections`, `re`).

