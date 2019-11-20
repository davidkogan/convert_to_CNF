import collections
import collections.abc
# DO NOT CHANGE THIS FILE

# DO NOT CHANGE THIS CLASS
class Expr:
    """A Boolean Expression with an operator and 0 or more arguments.
    op is a str like '|' or '~';
    Expr('x') or Symbol('x') creates a symbol
    Expr('~', x) creates a unary expression;
    Expr('&', A, B) creates a binary expression.

    The follwing in this class are "Special method names", which is Python’s operator overloading mechanism
    We overload them so that we can use Python's infix(&,|) and prefix(~) operators to construct Boolean Expressions
    (https://docs.python.org/3/reference/datamodel.html#special-method-names)
    """

    def __init__(self, op, *args):
        self.op = str(op)
        self.args = args

    # Operator overloads
    def __invert__(self):
        return Expr('~', self)

    def __and__(self, rhs):
        return Expr('&', self, rhs)

    def __or__(self, rhs):
        # Allow both P | Q, and P |'==>'| Q.
        if isinstance(rhs, Expression):
            return Expr('|', self, rhs)
        else:
            return PartialExpr(rhs, self)

    # Reverse operator overloads
    def __rand__(self, lhs):
        return Expr('&', lhs, self)

    def __ror__(self, lhs):
        return Expr('|', lhs, self)

    # Equality, xor, hash, and repr
    def __eq__(self, other):
        """x == y' evaluates to True or False; does not build an Expr."""
        return isinstance(other, Expr) and self.op == other.op and self.args == other.args

    def __xor__(self, rhs):
        return Expr('^', self, rhs)

    def __hash__(self):
        return hash(self.op) ^ hash(self.args)

    # Overload __repr__() to look neaterer when printing
    def __repr__(self):
        op = self.op
        args = [str(arg) for arg in self.args]
        if op.isidentifier():  # f(x) or f(x, y)
            return '{}({})'.format(op, ', '.join(args)) if args else op
        elif len(args) == 1:  # -x or -(x + 1)
            return op + args[0]
        else:  # (x - y)
            opp = (' ' + op + ' ')
            return '(' + opp.join(args) + ')'

    # So that Expr is callable
    def __call__(self, *args):
        if self.args:
            raise ValueError('can only do a call for a Symbol, not an Expr')
        else:
            return Expr(self.op, *args)

# DO NOT CHANGE THIS CLASS
class PartialExpr:
    # Given 'P |'==>'| Q, first form PartialExpr('==>', P), then combine with Q.
    def __init__(self, op, lhs):
        self.op, self.lhs = op, lhs

    def __or__(self, rhs):
        return Expr(self.op, self.lhs, rhs)

    def __repr__(self):
        return "PartialExpr('{}', {})".format(self.op, self.lhs)


Number = (int, float, complex)
Expression = (Expr, Number)


def expr(x):
    # expr parse a string into an Expr,
    # it helps to create an Expr by treating ==> in the input string as an infix |'==>'|, as is <=>.
    return eval(expr_handle_infix_ops(x), defaultkeydict(Symbol)) if isinstance(x, str) else x


def expr_handle_infix_ops(x):
    # Given a str, return a new str with ==> replaced by |'==>'|, etc.
    """Example: 
    >>> expr_handle_infix_ops('P ==> Q')
    "P |'==>'| Q"
    """
    for op in '==> <=>'.split():
        x = x.replace(op, '|' + repr(op) + '|')
    return x

# DO NOT CHANGE THIS CLASS
class defaultkeydict(collections.defaultdict):
    def __missing__(self, key):
        self[key] = result = self.default_factory(key)
        return result

def Symbol(name):
    # A Symbol is just an Expr with no args."""
    return Expr(name)

def symbols(names):
    # Return a tuple of Symbols; names is a comma/whitespace delimited str."""
    return tuple(Symbol(name) for name in names.replace(',', ' ').split())


def no_heuristic(symbols, clauses):
    return first(symbols), True


def is_symbol(s):
    # A string s is a symbol if it starts with an alphabetic char.
    """Example:
    >>> is_symbol('CS5112')
    True
    """
    return isinstance(s, str) and s[:1].isalpha()


def associate(op, args):
    # Given an associative op, return an flattened expression with the same meaning as Expr(op, *args)
    # with nested instances of the same op popped up to the top.
    """Example:
    >>> associate('&', [(A&B),(B|C),(B&C)])
    (A & B & (B | C) & B & C)
    >>> associate('|', [A|(B|(C|(A&B)))])
    (A | B | C | (A & B))
    """
    args = dissociate(op, args)
    if len(args) == 0:
        return _op_identity[op]
    elif len(args) == 1:
        return args[0]
    else:
        return Expr(op, *args)


def dissociate(op, args):
    # Given an associative op, return a flattened list result such that Expr(op, *result) means the same as Expr(op, *args).
    """Example:
    >>> dissociate('&', [A & B])
    [A, B]
    """
    result = []

    def collect(subargs):
        for arg in subargs:
            if arg.op == op:
                collect(arg.args)
            else:
                result.append(arg)
    collect(args)
    return result


def conjuncts(s):
    return dissociate('&', [s])


def disjuncts(s):
    return dissociate('|', [s])


def prop_symbols(x):
    # Return the set of all propositional symbols in x.
    if not isinstance(x, Expr):
        return set()
    elif is_prop_symbol(x.op):
        return {x}
    else:
        return {symbol for arg in x.args for symbol in prop_symbols(arg)}


def is_prop_symbol(s):
    # A proposition logic symbol is an initial-uppercase string.
    """Example:
    >>> is_prop_symbol('exe'):              
    False
    """
    return is_symbol(s) and s[0].isupper()


def pl_true(exp, assignment={}):
    # Return True if the propositional logic expression is true in the assignment,
    # and False if it is false. If the assignment does not specify the value for
    # every proposition, this may return None to indicate 'not obvious';
    # this may happen even when the expression is tautological.
    """Example:
    >>> pl_true(P, {}) is None
    True
    """
    if exp in (True, False):
        return exp
    op, args = exp.op, exp.args
    if is_prop_symbol(op):
        return assignment.get(exp)
    elif op == '~':
        p = pl_true(args[0], assignment)
        if p is None:
            return None
        else:
            return not p
    elif op == '|':
        result = False
        for arg in args:
            p = pl_true(arg, assignment)
            if p is True:
                return True
            if p is None:
                result = None
        return result
    elif op == '&':
        result = True
        for arg in args:
            p = pl_true(arg, assignment)
            if p is False:
                return False
            if p is None:
                result = None
        return result
    p, q = args
    if op == '==>':
        return pl_true(~p | q, assignment)
    elif op == '<==':
        return pl_true(p | ~q, assignment)
    pt = pl_true(p, assignment)
    if pt is None:
        return None
    qt = pl_true(q, assignment)
    if qt is None:
        return None
    if op == '<=>':
        return pt == qt
    elif op == '^':  # xor or 'not equivalent'
        return pt != qt
    else:
        raise ValueError('Illegal operator in logic expression' + str(exp))


def find_pure_symbol(symbols, clauses):
    # Find a symbol and its value if it appears only as a positive literal
    # (or only as a negative) in clauses.
    """Example:
    >>> find_pure_symbol([A, B, C], [A|~B,~B|~C,C|A])
    (A, True)
    """
    for s in symbols:
        found_pos, found_neg = False, False
        for c in clauses:
            if not found_pos and s in disjuncts(c):
                found_pos = True
            if not found_neg and ~s in disjuncts(c):
                found_neg = True
        if found_pos != found_neg:
            return s, found_pos
    return None, None


def find_unit_clause(clauses, assignment):
    # Find a forced assignment if possible from a clause with only 1
    # variable not bound in the assignment.
    """Example:
    >>> find_unit_clause([A|B|C, B|~C, ~A|~B], {A:True})
    (B, False)
    """
    for clause in clauses:
        P, value = unit_clause_assign(clause, assignment)
        if P:
            return P, value
    return None, None


def unit_clause_assign(clause, assignment):
    # Return a single variable/value pair that makes clause true in
    # the assignment, if possible.
    """
    >>> unit_clause_assign(A|B|C, {A:True})
    (None, None)
    >>> unit_clause_assign(B|~C, {A:True})
    (None, None)
    >>> unit_clause_assign(~A|~B, {A:True})
    (B, False)
    """
    P, value = None, None
    for literal in disjuncts(clause):
        sym, positive = inspect_literal(literal)
        if sym in assignment:
            if assignment[sym] == positive:
                return None, None  # clause already True
        elif P:
            return None, None  # more than 1 unbound variable
        else:
            P, value = sym, positive
    return P, value


def inspect_literal(literal):
    # The symbol in this literal, and the value it should take to make the literal true.
    """Example:
    >>> inspect_literal(P)
    (P, True)
    >>> inspect_literal(~P)
    (P, False)
    """
    if literal.op == '~':
        return literal.args[0], False
    else:
        return literal, True


def remove_all(item, seq):
    # Return a copy of seq (or string) with all occurrences of item removed.
    if isinstance(seq, str):
        return seq.replace(item, '')
    elif isinstance(seq, set):
        rest = seq.copy()
        rest.remove(item)
        return rest
    else:
        return [x for x in seq if x != item]


def extend(s, var, val):
    # Copy dict s and extend it by setting var to val; return copy.
    s2 = s.copy()
    s2[var] = val
    return s2


def first(iterable, default=None):
    # Return the first element of an iterable; or default.
    return next(iter(iterable), default)


if __name__ == "__main__":

    s = expr('A & (B | C)')
    print(s.op)
    print(s.args)
    
