
def tokenize(char_iter):
    def is_delim(char):
        return char.isspace() or char in ['(', ')']

    acc = ''
    for char in char_iter:
        if is_delim(char):
            if len(acc) > 0: yield acc
            acc = ''
            if char == '(' or char == ')':
                yield char
        elif char == '?' or char == ':':
            if len(acc) > 0: yield acc
            acc = ''
            acc += char
        else:
            acc += char

