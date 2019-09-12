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

    Args:
      tokens = a list of strings that are the tokens of the program.
      context = an AbstractContext that understands the types and symbols in the program.
      index (default 0) = the index in the list to parse at.
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
        if context.is_abstraction_fn(calling):
            #TODO: (def! <name> (<arg list (potentially with types)>) <body>)
            # arg list is optional -- no arg list means that it's just a constant value
            if tokens[index] == '(':
                raise ValueError("Function name must be raw identifier")
            name = tokens[index]
            index = index + 1
            if index >= len(tokens):
                raise ValueError("Function definition incomplete")

            pass
        else:
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
