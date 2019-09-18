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
    assert ctx.literal('foo') == 9.0
    assert ctx.literal('bar') == "LOL spaces ain't supported"
    expect_value_error(lambda: ctx.literal('baz'))

def test_base_call():
    literals = {
        'foo': (9, ctxs.Float()),
        'bar': ("LOL spaces ain't supported", ctxs.String()),
        'fn': ((lambda x: x, 'fn'), ctxs.Function((None, None))),
        'inc': ((lambda x: x + 1, 'inc'), ctxs.Function((ctxs.Float(), ctxs.Float())))
    }
    ctx = ctxs.BaseContext(tok.evaluate, literals)
    expect_value_error(lambda: ctx.call('halp'))
    expect_value_error(lambda: ctx.call('foo'))
    expect_value_error(lambda: ctx.call('fn'))
    expect_value_error(lambda: ctx.call(literals['fn'], 1, 2))
    expect_value_error(lambda: ctx.call(literals['inc'], 1, 2))
    expect_value_error(lambda: ctx.call(literals['inc'], '1, 2'))
    assert abs(ctx.call(literals['inc'], 1.5) - 2.5) < 0.01
    assert ctx.call(literals['fn'], 'heh') == 'heh'
    assert ctx.call(literals['fn'], 5.6) == 5.6

def test_base_type_getter():
    ctx = ctxs.BaseContext(tok.evaluate)
    assert ctx.get_type(None, 'string') == ctxs.String()
    assert ctx.get_type(None, 'float') == ctxs.Float()
    assert ctx.get_type(None, '->', ctxs.Float(), ctxs.Float())\
            == ctxs.Function((ctxs.Float(), ctxs.Float()))
    expect_value_error(lambda: ctx.get_type(None, 'not-a-type'))

def test_base_make_abstraction():
    literal = {
        '+': ((lambda x, y: x + y, '+'), ctxs.Function((None, None, None)))
    }
    ctx = ctxs.BaseContext(tok.evaluate, literal)
    abstraction = ctx.make_abstraction('inc', (('x', None, ctxs.Float()),), ['(', '+', 'x', '1', ')'])
    assert abs(abstraction[0][0](1.5) - 2.5) < 0.01
    assert ctx.lexical_vars['inc'] == abstraction
    assert ctx.lexical_vars['inc'][1] == ctxs.Function((ctxs.Float(), None))

# TODO: if needs to be a SpecialForm, so we have to parse those more generally before trying this sort of
# thing.
# def test_base_recursion():
#     program = """
# (def! triangle-sum (x?F:float) (if (= x 0) 0 (+ x (triangle-sum (- x 1)))))
#     """
#     literals = {
#         '-': ((lambda x, y: x - y, '-'), ctxs.Function(ctxs.Float(), ctxs.Float(), ctxs.Float())),
#         '+': ((lambda x, y: x + y, '+'), ctxs.Function(ctxs.Float(), ctxs.Float(), ctxs.Float())),
#         'if': ((lambda c, t, e: 
#     }
