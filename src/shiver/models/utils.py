from collections.abc import Iterable

def flatten_list(xs):
    """ Flattens a list of lists
    list(flatten_list([[['test']],1,2,[3,4,[5,6]]])) will yield ['test', 1, 2, 3, 4, 5, 6]
    """
    if isinstance(xs, str):
        yield xs
    else:
        for x in xs:
            if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
                yield from flatten(x)
            else:
                yield x
