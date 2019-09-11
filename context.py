"""
Defines the base context which
includes the general interfaces for defining
contexts and types therein.

The abstract class is with the tokenizer for
convenience.
"""
from enum import Enum

from tokenizer import AbstractContext

class BaseContext(AbstractContext):
    def __init__(self, fns = {}, lexical_vars = {}, semantics = {}, types = {}):
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
        return self.fns[fn](*args)
    def get_semantics(self, name):
        return self.semantics[name]
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
