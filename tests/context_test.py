import tokenizer as tok
import context as ctxs
import sem_lang_types as types

import pytest

from testing_utils import *

def test_base_literal():
    literals = {
        'foo': types.Float('foo', 9.5),
        'bar': types.String('bar', "LOL spaces ain't supported")
    }
    ctx = ctxs.BaseContext(tok.evaluate, tok.parse_type, literals)
    assert is_type_with_binding(ctx.literal('9.5'), types.Float, 9.5)
    assert is_type_with_binding(ctx.literal('"This is not yet OK by the tokenizer"'),
            types.String, "This is not yet OK by the tokenizer")
    assert is_type_with_binding(ctx.literal('foo'), types.Float, 9.5)
    assert is_type_with_binding(ctx.literal('bar'), types.String, "LOL spaces ain't supported")
    expect_value_error(lambda: ctx.literal('baz'))

def test_base_call():
    literals = {
        'foo': types.Float('foo', 9),
        'bar': types.String('bar', "LOL spaces ain't supported"),
        'fn': types.Function((types.Type(), types.Type()), lambda x: x, 'fn'),
        'inc': types.Function((types.Float(), types.Float()), lambda x: x + 1, 'inc'),
    }
    ctx = ctxs.BaseContext(tok.evaluate, tok.parse_type, literals)
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
    ctx = ctxs.BaseContext(tok.evaluate, tok.parse_type, dict())
    assert ctx.get_type(None, 'string') == types.String()
    assert ctx.get_type(None, 'float') == types.Float()
    assert ctx.get_type(None, '->', types.Float(), types.Float())\
            == types.Function((types.Float(), types.Float()), lambda x: x)
    expect_value_error(lambda: ctx.get_type(None, 'not-a-type'))
