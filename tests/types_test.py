import tokenizer as tok
import context as ctxs
import sem_lang_types as types

import pytest

from testing_utils import *

def test_equality():
    # やれやれ、線分試するは無理
    assert types.Type() == types.Type()
    assert types.Float() == types.Float()
    assert types.String() == types.String()
    assert types.Function((types.Float(),), None) == types.Function((types.Float(),), None)

def test_validation():
    assert types.Float().validate_py(0.5)
    assert not types.Float().validate_py("literal every other possible py thing")
    assert types.String().validate_py("literal every other possible py thing")
    assert types.String().validate_py(0.5)
    assert types.Bool().validate_py(True)
    assert types.Bool().validate_py(0.5)
    assert types.Type().validate_py("absolutely anything")
