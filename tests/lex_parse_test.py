import tokenizer as tok

import pytest

def test_basic_tokens():
    assert list(tok.tokenize("(+ 1 1)")) == ['(', '+', '1', '1', ')']
    assert list(tok.tokenize("(+ 121 1 (* 2 3))")) == ['(', '+', '121', '1', '(', '*', '2', '3', ')', ')']
    assert list(tok.tokenize("(+ 1 1)?F:int")) == ['(', '+', '1', '1', ')', '?F', ':int']
    assert list(tok.tokenize("(+ 1 1) ?F :int")) == ['(', '+', '1', '1', ')', '?F', ':int']

