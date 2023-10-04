"""Common utility functions"""

from collections.abc import Iterable


def flatten_list(xlst):
    """Flattens a list of lists
    list(flatten_list([[['test']],1,2,[3,4,[5,6]]])) will yield ['test', 1, 2, 3, 4, 5, 6]
    """
    if isinstance(xlst, str):
        yield xlst
    else:
        for lst in xlst:
            if isinstance(lst, Iterable) and not isinstance(lst, (str, bytes)):
                yield from flatten_list(lst)
            else:
                yield lst
