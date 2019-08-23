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

class AbstractContext:
    def literal(self, token):
        pass
    def call(self, fn, *args):
        pass
    def get_semantics(self, name):
        pass
    def get_type(self, semantics, name):
        pass
    def validate_type(self, literal, semantics, type):
        pass

def parse_type(tokens, context, index):
    return 0, 0

def evaluate(tokens, context, index = 0):
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
        if context.validate_type(evaled, semantics, typ):
            return evaled, index
    else:
        return evaled, index + 1
