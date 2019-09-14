import tokenizer as tok

from functools import reduce
import pytest

def test_basic_tokens():
    assert list(tok.tokenize("(+ 1 1)")) == ['(', '+', '1', '1', ')']
    assert list(tok.tokenize("(+ 121 1 (* 2 3))")) == ['(', '+', '121', '1', '(', '*', '2', '3', ')', ')']
    assert list(tok.tokenize("(+ 1 1)?F:int")) == ['(', '+', '1', '1', ')', '?', 'F', ':', 'int']
    assert list(tok.tokenize("(+ 1 1) ?F :int")) == ['(', '+', '1', '1', ')', '?', 'F', ':', 'int']
    assert list(tok.tokenize("(+ (* 1 1 1) 1)")) == ['(', '+', '(', '*', '1', '1', '1', ')', '1', ')']

class PlusTimesCtx:
    def literal(self, val):
        if not val.isdigit():
            if val in ['*', '+']:
                return val
            raise ValueError("Nan")
        return int(val)
    def call(self, fn, args):
        if fn not in ['+', '*']:
            raise ValueError("Not a function")
        return reduce(lambda x, y: {'+': x + y, '*': x * y}[fn], args, {'+': 0, '*': 1}[fn])
    def get_semantics(self, name):
        return name
    def get_type(self, semantics, name, *generic_args):
        return name
    def validate_type(self, l, semantics, typ):
        return (typ == 'int' and l not in ['+', '*']) or (typ == 'fn' and l in ['+', '*'])
    def is_abstraction_fn(self, name):
        return False

def test_eval():
    pt = PlusTimesCtx()
    assert tok.evaluate(list(tok.tokenize("(+ 1 1)")), pt)[0] == 2
    tm = list(tok.tokenize("(+ (* 1 1 1) 1)"))
    assert tok.evaluate(tm, pt)[0] == 2

def test_types():
    pt = PlusTimesCtx()
    assert tok.evaluate(list(tok.tokenize("(+ 1 1)?F:int")), pt)[0] == 2
    assert tok.evaluate(list(tok.tokenize("(+?F:(fn ?F:int ?F:int) 1 1)?F:int")), pt)[0] == 2
