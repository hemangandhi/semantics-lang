"""
Basic lexer and parser for the sematics-lang
"""

def tokenize(char_iter):
    """
    Given an input stream (any iterator over strs),
    tokenizes the input as per the tokens in the readme.
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

def prepend_to_iter(prepend, it):
    yield prepend
    yield from it

def evaluate(tokens, context):
    try:
        t = next(tokens)
        if t == '(':
            calling = evaluate(tokens, context)
            nt = next(tokens)
            args = []
            while nt != ')':
                args.append(evaluate(prepend_to_iter(nt, tokens), context))
                nt = next(tokens)
            return context.call(calling, args)
        else:
            return context.literal(t)
    except StopIteration:
        raise ValueError("Expected a token")
