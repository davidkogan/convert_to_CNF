from helpers import *

# DO NOT CHANGE THIS FILE

# dpll is a CNF-SAT solver
# you don't really need to understand how this works to finish HW3
def dpll(clauses, symbols, assignment, heuristic=no_heuristic):
    unknown_clauses = []
    for c in clauses:
        val = pl_true(c, assignment)
        if val is False:
            return False
        if val is None:
            unknown_clauses.append(c)
    if not unknown_clauses:
        return assignment
    P, value = find_pure_symbol(symbols, unknown_clauses)
    if P:
        return dpll(clauses, remove_all(P, symbols), extend(assignment, P, value), heuristic)
    P, value = find_unit_clause(clauses, assignment)
    if P:
        return dpll(clauses, remove_all(P, symbols), extend(assignment, P, value), heuristic)
    P, value = heuristic(symbols, unknown_clauses)
    return (dpll(clauses, remove_all(P, symbols), extend(assignment, P, value), heuristic) or
            dpll(clauses, remove_all(P, symbols), extend(assignment, P, not value), heuristic))
