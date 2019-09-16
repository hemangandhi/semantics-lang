import tokenizer as tok
import context as ctxs

import pytest

def test_context_type_checker():
    ctx = ctxs.BaseContext(tok.evaluate)
    assert ctx.check_type(9.5, ctxs.Float)
    assert ctx.check_type("foo", ctxs.String)
    assert ctx.check_type("def!", ctxs.SpecialForm)
    assert ctx.check_type(lambda x:  x, ctxs.Function)
