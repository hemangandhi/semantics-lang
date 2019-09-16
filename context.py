"""
Defines the base context which
includes the general interfaces for defining
contexts and types therein.
"""

class AbstractContext:
    """
    Abstract base for all the contexts.
    Doesn't include any of the functionality,
    just the interface. See `context.py`
    for the basic implementation.

    Recall that the context is a part of
    an evaluator, not a compiler.
    """
    def literal(self, token: str):
        """
        Given a literal token -- with no
        type context.
        """
        pass
    def call(self, fn: str, *args):
        """
        Function call on evaluated arguments.

        Args:
          fn: str = is an unevaluated string literal
          args: the evaluated arguments passed to the function
        """
        pass
    def get_semantics(self, name: str):
        """
        Get the semantics of a name.
        This will be passed back to the context.
        """
        pass
    def get_type(self, semantics, name, *generic_args):
        """
        Gets the type in the semantics with the name passed in.
        Generic arguments are also passed in with semantics.

        Args:
          semantics = a type of semantics returned by `self.get_semantics`.
          name: str = the name of the type at the root.
          generic_args = types that are being passed in as generic parameters.
        Returns:
          any type tag
        """
        pass
    def validate_type(self, literal, semantics, type) -> bool:
        """
        Given an evaluated literal, ensures that it is of the type
        an valid in the semantics. Note that both the semantics and type
        will have been from `get_semantics` and `get_type` respectively.

        Returns:
          bool = whether the evaluated literal should type check.
        """
        pass
    def is_abstraction_fn(self, literal) -> bool:
        """
        Given an evaled literal, get whether it refers to the abstraction
        creator in this context.

        Returns:
          bool = whether the evaluated literal should create an abstraction.
        """
        pass
    def make_abstraction(self, name, args, body):
        """
        Given a name, args, and a body, make a function.
        The body is a list of strings that can be passed to evaluate to
        call the function with a context where the arguments are bound.
        Binding has to do with semantics, so the bindings are manged therein.

        args are paired with any semantics and type annotations present
        (None if there is no annotation for the argument).

        Returns: anything the context will think is a function.
        (in case it's also being invoked on the spot)
        """
        pass

# For a basic language with functions, the only generic type is the function type
# denoted -> for us. It looks like this: `data Type = SpecialForm | Float | String | Function [Type]`
class Type:
    pass

class Float(Type):
    pass

class String(Type):
    pass

class Function(Type):
    def __init__(self, inners):
        self.gen = inners

class SpecialForm(Type):
    pass

# Now for the actual context...

class BaseContext(AbstractContext):
    def __init__(self, evaluator, lexical_vars = {'def!': ('def!', SpecialForm())}):
        #shame the plural of semantics is semantics... eh, semantics
        self.lexical_vars = lexical_vars
        self.eval = evaluator
    def check_type(self, value, typ):
        if type(typ) == Float:
            return type(value) == float
        if type(typ) == String:
            return type(value) == str
        if type(typ) == SpecialForm:
            return value == 'def!'
        if type(typ) == Function:
            # Escape hatch 1: don't know how to assert
            # recursive details about types
            return hasattr(value, '__call__')
        # Escape hatch 2: no annotation means OK type
        return True
    def literal(self, token):
        if token in self.lexical_vars:
            return self.lexical_vars[token]
        elif token.startswith('"') and token.endswith('"'):
            return token[1:len(token) - 1]
        else:
            return float(token)
    def call(self, fn, *args):
        if fn not in self.lexical_vars:
            raise ValueError("Undefined lexical variable " + fn)
        if type(self.lexical_vars[fn][1]) != Function:
            raise ValueError("The lexical variable provided in not a function: " + fn)
        fn_type = self.lexical_vars[fn][1]
        if len(args) != len(fn_type.gen) - 1:
            raise ValueError("Arity incorrect, expected {} args.".format(len(fn_type.gen) - 1))
        if any(not self.check_type(arg, typ) for arg, typ in zip(args, fn_type.gen[:-1])):
            raise ValueError("Type error in function invocation of {} and args {}".format(fn, args))
        return self.lexical_vars[fn][0](*args)
    def get_semantics(self, name):
        # TODO: have semantics definitions
        return None
    def get_type(self, semantics, name, *args):
        if name == 'string':
            return String()
        if name == 'float':
            return Float
        if name == '->':
            return Function(*args)
        raise ValueError("Unknown type {} passed in".format(name))
    def validate_type(self, literal, semantics, typ):
        return self.check_type(literal, typ)
    def is_abstraction_fn(self, literal):
        return literal == 'def!'
    def make_abstraction(self, name, args, body):
        def calling_thing(*args_passed):
            inner_lex = self.lexical_vars.copy()
            for value, arg_info in zip(args_passed, args):
                inner_lex[arg_info[0]] = (value, arg_info[2])
            return self.eval(body, BaseContext(self.eval, inner_lex))
        self.lexical_vars[name] = (calling_thing, Function(tuple(map(lambda a: a[2], args) + (None,))))
        return calling_thing
