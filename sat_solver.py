# TODO: Your name, Cornell NetID
# TODO: Your Partner's name, Cornell NetID

from helpers import *
from cnf_sat_solver import dpll

# DO NOT CHANGE SAT_solver 
# Convert to Conjunctive Normal Form (CNF)
"""
>>> to_cnf_gadget('~(B | C)')
(~B & ~C)
"""
def to_cnf_gadget(s):
    s = expr(s)
    if isinstance(s, str):
        s = expr(s)
    step1 = parse_iff_implies(s)  # Steps 1
    step2 = deMorgansLaw(step1)  # Step 2
    return distibutiveLaw(step2)  # Step 3

# ______________________________________________________________________________
# STEP1: if s has IFF or IMPLIES, parse them

# TODO: depending on whether the operator contains IMPLIES('==>') or IFF('<=>'),
# Change them into equivalent form with only &, |, and ~ as logical operators
# The return value should be an Expression (e.g. ~a | b )

# Hint: you may use the expr() helper function to help you parse a string into an Expr
# you may also use the is_symbol() helper function to determine if you have encountered a propositional symbol
def parse_iff_implies(s):
    # TODO: write your code here, change the return values accordingly

    def helper(s):
        if not s:
            return None

        op = s.op
        args = s.args

        if is_symbol(op):
            return Expr(op)

        else:
	    #Not
            if op == '~':
                return (helper(args[0])).__invert__()
	    #Or
            elif op == '|':
                left = helper(args[0])
                right = helper(args[1])
                return left.__or__(right)
	    #And
            elif op == '&':
                left = helper(args[0])
                right = helper(args[1])
                return left.__and__(right)
	    #Iff
            elif op == '<=>':
                left = helper(args[0])
                right = helper(args[1])
                newleft = Expr('==>', expr(left), expr(right))
                newright = Expr('==>', expr(right), expr(left))
                return newleft.__and__(newright)
	    #Implies
            elif op == '==>':
                left = helper(args[0])
                right = helper(args[1])
                newleft = (helper(left)).__invert__()
                newright = right
                return newleft.__or__(newright)

    return helper(helper(s))

# ______________________________________________________________________________
# STEP2: if there is NOT(~), move it inside, change the operations accordingly.


""" Example:
>>> deMorgansLaw(~(A | B))
(~A & ~B)
"""

# TODO: recursively apply deMorgansLaw if you encounter a negation('~')
# The return value should be an Expression (e.g. ~a | b )

# Hint: you may use the associate() helper function to help you flatten the expression
# you may also use the is_symbol() helper function to determine if you have encountered a propositional symbol
def deMorgansLaw(s):
    # TODO: write your code here, change the return values accordingly
    return Expr(s.op, *args)

# ______________________________________________________________________________
# STEP3: use Distibutive Law to distribute and('&') over or('|')


""" Example:
>>> distibutiveLaw((A & B) | C)
((A | C) & (B | C))
"""

# TODO: apply distibutiveLaw so as to return an equivalent expression in CNF form
# Hint: you may use the associate() helper function to help you flatten the expression
def distibutiveLaw(s):
    # TODO: write your code here, change the return values accordingly
    return Expr(s.op, *args)


# ______________________________________________________________________________

# DO NOT CHANGE SAT_solver 
# Check satisfiability of an arbitrary looking Boolean Expression.
# It returns a satisfying assignment(Non-deterministic, non exhaustive) when it succeeds.
# returns False if the formula is unsatisfiable
# Don't need to care about the heuristic part


""" Example: 
>>> SAT_solver(A |'<=>'| B) == {A: True, B: True}
True
"""

""" unsatisfiable example: 
>>> SAT_solver(A & ~A )
False
"""
def SAT_solver(s, heuristic=no_heuristic):
    return dpll(conjuncts(to_cnf_gadget(s)), prop_symbols(s), {}, heuristic)


if __name__ == "__main__":

# Initialization
    A, B, C, D, E, F = expr('A, B, C, D, E, F')
    P, Q, R = expr('P, Q, R')

# Shows alternative ways to write your expression
    assert SAT_solver(A | '<=>' | B) == {A: True, B: True}
    assert SAT_solver(expr('A <=> B')) == {A: True, B: True}

# Some unsatisfiable examples
    assert SAT_solver(P & ~P) is False
    # The whole expression below is essentially just (A&~A)
    assert SAT_solver((A | B | C) & (A | B | ~C) & (A | ~B | C) & (A | ~B | ~C) & (
        ~A | B | C) & (~A | B | ~C) & (~A | ~B | C) & (~A | ~B | ~C)) is False

# This is the same example in the instructions.
    # Notice that SAT_solver's return value  is *Non-deterministic*, and *Non-exhaustive* when the expression is satisfiable,
    # meaning that it will only return *a* satisfying assignment when it succeeds.
    # If you run the same instruction multiple times, you may see different returns, but they should all be satisfying ones.
    result = SAT_solver((~(P | '==>' | Q)) | (R | '==>' | P))
    assert pl_true((~(P | '==>' | Q)) | (R | '==>' | P), result)

    assert pl_true((~(P | '==>' | Q)) | (R | '==>' | P), {P: True})
    assert pl_true((~(P | '==>' | Q)) | (R | '==>' | P), {Q: False, R: False})
    assert pl_true((~(P | '==>' | Q)) | (R | '==>' | P), {R: False})

# Some Boolean expressions has unique satisfying solutions
    assert SAT_solver(A & ~B & C & (A | ~D) & (~E | ~D) & (C | ~D) & (~A | ~F) & (E | ~F) & (~D | ~F) &
                      (B | ~C | D) & (A | ~E | F) & (~A | E | D)) == \
        {B: False, C: True, A: True, F: False, D: True, E: False}
    assert SAT_solver(A & B & ~C & D) == {C: False, A: True, D: True, B: True}
    assert SAT_solver((A | (B & C)) | '<=>' | ((A | B) & (A | C))) == {
        C: True, A: True} or {C: True, B: True}
    assert SAT_solver(A & ~B) == {A: True, B: False}

# The order in which the satisfying variable assignments get returned doen't matter.
    assert {A: True, B: False} == {B: False, A: True}
    print("No assertion errors found so far")
