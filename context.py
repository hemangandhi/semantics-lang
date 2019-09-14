"""
Defines the base context which
includes the general interfaces for defining
contexts and types therein.

The abstract class is with the tokenizer for
convenience.
"""
from enum import Enum

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

class BaseContext(AbstractContext):
    def __init__(self,
            # None of these defaults make much sense...
            fns = lambda f: lambda g: None,
            lexical_vars = {},
            semantics = lambda n: lambda t: t,
            types = lambda n, a: None):
        #shame the plural of semantics is semantics... eh, semantics
        self.fns = fns
        self.lexical_vars = lexical_vars
        self.semantics = semantics
        self.types = types
    def literal(self, token):
        if token in self.lexical_vars:
            return self.lexical_vars[token]
        elif token.startswith('"') and token.endswith('"'):
            return token[1:len(token) - 1]
        else:
            return float(token)
    def call(self, fn, *args):
        return self.fns(fn)(*args)
    def get_semantics(self, name):
        return self.semantics(name)
    def get_type(self, semantics, name, *args):
        return self.types(name, args)
    def validate_type(self, literal, semantics, typ):
        return semantics(typ, literal)


# For a basic language with functions, the only generic type is the function type
# denoted -> for us. (So Haskell's int -> int -> int would be ?F:(-> ?F:int ?F:(-> ?F:int ?F:int)))

class Type(Enum):
    """
    Half-assed ADT for the types in the basic language with functions.
    Haskell: data Type = Float | String | Function Type Type
    """
    FLOAT = (())
    STRING = (())
    FUNCTION = ((None, None))
    def __init__(self, generics):
        self.gen = generics
    def validate_literal(self, literal):
        if self == Type.FLOAT:
            return type(literal) == float
        elif self == Type.STRING:
            return type(literal) == str
        else:
            # TODO: have an actual function type that... works (god damn I want ADTs)
            return hasattr(literal, '__call__')
    @staticmethod
    def from_str(name, args):
        if name == 'string':
            if len(args) > 0:
                raise TypeError("Cannot pass generic arguments to string type")
            return Type.STRING
        elif name == 'float':
            if len(args) > 0:
                raise TypeError("Cannot pass generic arguments to float type")
            return Type.FLOAT
        elif name == "->":
            if len(args) != 2:
                raise TypeError("-> type takes precisely 2 parameters!!")
            fn = Type.FUNCTION
            fn.gen = (args[0], args[1])
            return fn
