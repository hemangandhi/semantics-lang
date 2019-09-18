import tokenizer as tok
import context as ctxs

import pytest

def expect_value_error(fn):
    try:
        fn()
    except ValueError:
        return
    else:
        assert False

def test_base_check_type():
    ctx = ctxs.BaseContext(tok.evaluate)
    assert ctx.check_type(9.5, ctxs.Float())
    assert ctx.check_type("foo", ctxs.String())
    assert ctx.check_type("def!", ctxs.SpecialForm())
    assert ctx.check_type(lambda x: x, ctxs.Function(()))

def test_base_literal():
    literals = {
        'foo': (9.0, ctxs.Float()),
        'bar': ("LOL spaces ain't supported", ctxs.String())
    }
    ctx = ctxs.BaseContext(tok.evaluate, literals)
    assert type(ctx.literal('9.5')) == float
    assert type(ctx.literal('"This is not yet OK by the tokenizer"')) == str
    assert ctx.literal('foo') == (9.0, ctxs.Float())
    assert ctx.literal('bar') == ("LOL spaces ain't supported", ctxs.String())
    expect_value_error(lambda: ctx.literal('baz'))

def test_base_call():
    literals = {
        'foo': (9, ctxs.Float),
        'bar': ("LOL spaces ain't supported", ctxs.String()),
        'fn': (lambda x: x, ctxs.Function((None, None))),
        'inc': (lambda x: x + 1, ctxs.Function((ctxs.Float(), ctxs.Float())))
    }
    ctx = ctxs.BaseContext(tok.evaluate, literals)
    expect_value_error(lambda: ctx.call('halp'))
    expect_value_error(lambda: ctx.call('foo'))
    expect_value_error(lambda: ctx.call('fn'))
    expect_value_error(lambda: ctx.call('fn', 1, 2))
    expect_value_error(lambda: ctx.call('inc', 1, 2))
    expect_value_error(lambda: ctx.call('inc', '1, 2'))
    assert abs(ctx.call('inc', 1.5) - 2.5) < 0.01
    assert ctx.call('fn', 'heh') == 'heh'
    assert ctx.call('fn', 5.6) == 5.6
