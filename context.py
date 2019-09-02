"""
Defines the base context which
includes the general interfaces for defining
contexts and types therein.

The abstract class is with the tokenizer for
convenience.
"""

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
        return self.types[name](args)
    def validate_type(self, literal, semantics, typ):
        return semantics(typ, literal)

