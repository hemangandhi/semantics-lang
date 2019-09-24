def expect_value_error(fn):
    try:
        fn()
    except ValueError:
        return
    else:
        assert False

def is_type_with_binding(value, typ, binding):
    return value == typ() and value.binding == binding
