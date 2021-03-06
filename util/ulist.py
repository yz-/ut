__author__ = 'thorwhalen'

import numpy as np
import ut.util.var as util_var


def get_first_item_contained_in_intersection_of(find_first_item_of, in_iterable, default=None):
    for item in in_iterable:
        if item in find_first_item_of:
            return item
    return default

def ismember_lidx(A, B):
    # returns an A-length bitmap specifying what elements of A are in B
    return [i in B for i in A]


# def ismember(a, b):
#     # tf = np.in1d(a,b) # for newer versions of numpy
#     tf = np.array([i in b for i in a])
#     u = np.unique(a[tf])
#     index = np.array([(np.where(b == i))[0][-1] if t else 0 for i,t in zip(a,tf)])
#     return tf, index

def sort_as(sort_x, as_y, **sorted_kwargs):
    return [x for (y,x) in sorted(zip(as_y, sort_x), **sorted_kwargs)]


def all_true(x):
    """
    returns true if all entries of x are true
    """
    return np.all(x)
    # return len([xx for xx in x if xx==True]) == len(x)


def any_true(x):
    """
    returns true if any entries of x are true
    """
    return np.any(x)
    # return len([xx for xx in x if xx==True]) != 0


def to_str(x, sep=","):
    return sep.join(ascertain_list(x))


def ascertain_list(x):
    """
    ascertain_list(x) blah blah returns [x] if x is not already a list, and x itself if it's already a list
    Use: This is useful when a function expects a list, but you want to also input a single element without putting this
    this element in a list
    """
    if not isinstance(x, list):
        ## The "all but where it's a problem approach"
        if util_var.is_an_iter(x) and not isinstance(x, dict):
            x = list(x)
        else:
            x = [x]
        ## The (less safe) "just force what you want to do differently in those cases only" approach
        # if isinstance(x, np.ndarray):
        #     x = list(x)
        # else:
        #     x = [x]
    return x
