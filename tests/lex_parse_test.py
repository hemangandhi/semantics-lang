import tokenizer as tok

from functools import reduce
import pytest

def test_basic_tokens():
    assert list(tok.tokenize("(+ 1 1)")) == ['(', '+', '1', '1', ')']
    assert list(tok.tokenize("(+ 121 1 (* 2 3))")) == ['(', '+', '121', '1', '(', '*', '2', '3', ')', ')']
    assert list(tok.tokenize("(+ 1 1)?F:int")) == ['(', '+', '1', '1', ')', '?', 'F', ':', 'int']
    assert list(tok.tokenize("(+ 1 1) ?F :int")) == ['(', '+', '1', '1', ')', '?', 'F', ':', 'int']

def test_eval():
    class PlusTimesCtx:
        def literal(self, val):
            if not val.isdigit():
                raise ValueError("Nan")
            return int(val)
        def call(self, fn, args):
            if fn not in ['+', '*']:
                raise ValueError("Not a function")
            return reduce(lambda x, y: {'+': x + y, '*': x * y}[fn], args, {'+': 0, '*': 1}[fn])

    pt = PlusTimesCtx()
    assert tok.evaluate(tok.tokenize("(+ 1 1)"), pt) == 2
    assert tok.evaluate(tok.tokenize("(+ (* 1 1 1) 1)"), pt) == 2
