"""
Defines the base context which
includes the general interfaces for defining
contexts and types therein.
"""
from sem_lang_types import *

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
    def is_special_form(self, literal) -> bool:
        """
        Given an evaled literal, get whether it refers to the abstraction
        creator in this context.

        Returns:
          bool = whether the evaluated literal should create an abstraction.
        """
        pass
    def eval(self, tokens, index, name=None, finalize=False):
        """
        Evaluator used in parsing special forms.

        The name is a way to inform the context of which special form.
        It being none implies that the evaluation was started within a
        special form.

        finalize being true means that the context is expected to output
        a readable, more user-friendly type instead of a potentially internal
        one
        """
        pass
    def eval_type(self, tokens, index):
        pass

class BaseContext(AbstractContext):
    def __init__(self, evaluator, type_evaluator, lexical_vars):
        def bind_fn_off_special_form(name, args, body):
            def binding_fn(*py_args):
                new_vars = self.lexical_vars.copy()
                for arg in args:
                    new_vars[arg.name] = arg
                # allow recursion
                new_vars[name] = Function(binding_fn, args, name)
                new_context = BaseContext(evaluator, new_vars)
                return evaluator(body, new_context)
            self.lexical_vars[name] = Function(binding_fn, args, name)
            return self.lexical_vars[name]

        self.lexical_vars = lexical_vars
        self.evaler = evaluator
        self.type_evaler = type_evaluator
        self.special_forms = SpecialFormFactory(['(', ')', '?', ':'])
        self.special_forms('if!',
                lambda c, t, e: evaluator(t, self) if c else evaluator(e, self),
                SpecialFormSpec.EVALED_EXPR, SpecialFormSpec.EXPR, SpecialFormSpec.EXPR)
        self.special_forms('def!', bind_fn_off_special_form,
                SpecialFormSpec.NAME, SpecialFormSpec.LIST_OF_NAME, SpecialFormSpec.EXPR)

    def literal(self, token):
        if token in self.lexical_vars:
            return self.lexical_vars[token]
        elif token.startswith('"') and token.endswith('"'):
            return String(binding=token[1:len(token) - 1])
        else:
            return Float(binding=token)

    def call(self, fn, *args):
        if type(fn) != Function:
            raise ValueError("Non-function {} passed in".format(fn))
        return fn(*args)

    def get_semantics(self, name):
        # TODO: have semantics definitions
        return None
    def get_type(self, semantics, name, *args):
        if name == 'string':
            return String()
        if name == 'float':
            return Float()
        if name == '->':
            return Function(args, None)
        raise ValueError("Unknown type {} passed in".format(name))
    def validate_type(self, literal, semantics, typ):
        return typ == literal
    def is_special_form(self, literal):
        return literal in self.special_forms
    def eval(self, tokens, index, name=None, finalize=False):
        if name is None:
            rv = self.evaler(tokens, index)
        else:
            rv = self.special_forms[name].evaluate(tokens, self, index)
        if finalize:
            return rv.binding
        return rv
    def eval_type(self, tokens, index):
        return self.type_evaler(tokens, index)
