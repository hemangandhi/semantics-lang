"""
For a basic language with functions, the only generic type is the function type
denoted -> for us. It looks like this: `data Type = SpecialForm | Float | String | Function [Type]`.

Includes some validation functions for the types.

SpecialForm is another abstract base class under a type that also controls how it's evaluated.
For independence with the context and evaluator, none of the special forms that you'd expect are initialized here.
"""
from enum import Enum

class Type:
    def __init__(self):
        self.binding = None
    def __eq__(self, other):
        """
        Handy for type checking: ensures that the instances are the same type of type.
        """
        return type(self) == type(other)
    def validate_py(self, value):
        return False
    def bind(self, value):
        if not self.validate_py(value):
            raise ValueError("{} is not a valid {}".format(value, type(self)))
        self.binding = value

class Float(Type):
    def validate_py(self, value):
        return type(value) == float

class Bool(Type):
    def validate_py(self, value):
        return type(value) == bool

class String(Type):
    def validate_py(self, value):
        return type(value) == str

class Function(Type):
    def __init__(self, inners):
        self.gen = inners
    def __eq__(self, other):
        return type(self) == type(other) \
                and all(s == o or s is None or o is None for s, o in zip(self.gen, other.gen))
    def validate_py(self, value):
        return hasattr(value, '__call__')

class SpecialForm(Type):
    def evaluate(self, tokens, context, index):
        pass
    def validate_py(self, value):
        return False

class SpecialFormSpec(Enum):
    NAME = 1,
    LIST_OF_NAME = 2,
    EXPR = 3,
    EVALED_EXPR = 4

class SpecialFormFactory:
    def __init__(self, non_literals):
        self.forms = dict()
        self.non_literal = non_literals
    def __contains__(self, name):
        return name in self.forms
    def ensure_is_name(self, token):
        if token in self.non_literal:
            raise ValueError("Expected identifier not {}".format(token))
        try:
            f = float(token)
        except ValueError:
            return token
        else:
            raise ValueError("{} is not an identifier".format(token))
    def __call__(self, name, *allowed_sub_bodies):
        factory_self = self
        class DefinedSpecialForm(SpecialForm):
            def evaluate(self, tokens, context, index):
                bodies_idx = 0
                bindings = []
                while bodies_idx < len(allowed_sub_bodies):
                    if allowed_sub_bodies[bodies_idx] == SpecialFormSpec.NAME:
                        if index >= len(tokens):
                            raise ValueError("Expected identifier to complete {}".format(name))
                        bindings.append(factory_self.ensure_is_name(tokens[index]))
                        bodies_idx += 1
                    elif allowed_sub_bodies[bodies_idx] == SpecialFormSpec.LIST_OF_NAME:
                        names = []
                        if index >= len(tokens):
                            raise ValueError("Expected list of names to define {}".format(name))
                        if tokens[index] != '(':
                            raise ValueError("Expected '(' to open list of names")
                        index += 1
                        while index < len(tokens) and tokens[index] != ')':
                            names.append(factory_self.ensure_is_name(tokens[index]))
                            index += 1
                        if index >= len(tokens) or index[tokens] != ')':
                            raise ValueError("Expected ')' to end definition")
                        index += 1
                        bodies_idx += 1
                    elif allowed_sub_bodies[bodies_idx] == SpecialFormSpec.EXPR:
                        if index >= len(tokens):
                            raise ValueError("Expected value to be defined")
                        if tokens[index] != '(':
                            u_parse = [tokens[index]]
                        else:
                            num_parens = 1
                            next_index = index + 1
                            while num_parens > 0 and next_index < len(tokens):
                                if tokens[next_index] == '(':
                                    num_parens += 1
                                elif tokens[next_index] == ')':
                                    num_parens -= 1
                            if num_parens != 0:
                                raise ValueError("Mismatched parens in function definition")
                            index = next_index
                            u_parse = tokens[index: next_index + 1]
                        if index + 1 >= len(tokens) or tokens[index + 1] != ')':
                            raise ValueError("Expected closing parens to end function definition")
                        index = index + 2
                        bindings.append(u_parse)
                    elif allowed_sub_bodies[bodies_idx] == SpecialFormSpec.EVALED_EXPR:
                        bind, index = context.eval(tokens, index)
                if index + 1 >= len(tokens) or tokens[index + 1]:
                    raise ValueError("Expected closing paren")
                self.bind(bindings)
                return self, index + 2

        # indentation: outside the inner class now (factory_self and self are the same here)
        self.forms[name] = DefinedSpecialForm
        return DefinedSpecialForm
