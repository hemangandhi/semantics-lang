"""
Basic lexer and parser for the sematics-lang

Also the abstract base class for contexts
hereafter.
"""

def tokenize(char_iter):
    """
    Given an input stream (any iterator over strs),
    tokenizes the input as per the tokens in the readme.

    Yields:
      tokens
    """
    def is_delim(char):
        return char.isspace() or char in ['(', ')', '?', ':']

    acc = ''
    for char in char_iter:
        if is_delim(char):
            if acc != '':
                yield acc
            acc = ''
            if not char.isspace():
                yield char
        else:
            acc += char
    if acc != '':
        yield acc

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
          bool = whether the evaluated literal sound type check.
        """
        pass

def parse_type(tokens, context, index):
    """ return semantics, types, index """
    if tokens[index] != '?':
        raise ValueError("? prefix missing for ?semantics:type")
    if index + 1 >= len(tokens):
        raise ValueError("Expected semantics after ?")
    semantics = context.get_semantics(tokens[index + 1])
    if index + 2 >= len(tokens) or tokens[index + 2] != ':':
        raise ValueError("Need : to delimit semantics and type")
    if index + 3 >= len(tokens):
        raise ValueError("Expected type after :")
    if tokens[index + 3] == '(':
        if index + 4 >= len(tokens):
            raise ValueError("Expected type after (")
        base_type = tokens[index + 4]
        index += 5
        args = []
        while index < len(tokens) and tokens[index] != ')':
            sem, typ, index = parse_type(tokens, context, index)
            args.append((sem, typ))
        if index >= len(tokens) or tokens[index] != ')':
            raise ValueError("Expected )")
        return semantics, context.get_type(semantics, base_type, *args), index + 1
    else:
        return semantics, context.get_type(semantics, tokens[index + 3], []), index + 4

def evaluate(tokens, context, index = 0):
    """
    Evaluate the *list* of tokens in the context,
    starting at index provided.

    Raises: (Note that the context may raise exceptions too)
      ValueError = parsing issues with the token list or a type error.
    Returns:
      The evaluation of the code.
    """
    if index >= len(tokens):
        raise ValueError("Expected tokens")

    t = tokens[index]
    if t == '(':
        calling, index = evaluate(tokens, context, index + 1)
        args = []
        while tokens[index] != ')' and index < len(tokens):
            arg, index = evaluate(tokens, context, index)
            args.append(arg)
        if tokens[index] != ')':
            raise ValueError("Expected tokens")
        evaled = context.call(calling, args)
    else:
        evaled = context.literal(t)
    if index + 1 < len(tokens) and tokens[index + 1] == '?':
        semantics, typ, index = parse_type(tokens, context, index + 1)
        if not context.validate_type(evaled, semantics, typ):
            raise ValueError("type error in the code")
        return evaled, index
    else:
        return evaled, index + 1
