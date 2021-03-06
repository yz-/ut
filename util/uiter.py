import itertools

# These are itertools recipes taken from https://docs.python.org/2/library/itertools.html#recipes
# ... plus other stuff found here and there, plus my own sh**


# def chunker(seq, size):
#     return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


# def chunker(seq, size, start=0):
#         for i in itertools.count(start, size):
#             yield seq[i: i + size]


def all_subsets_of(iterable, include_empty_set=True):
    if include_empty_set is True:
        start = 0
    else:
        start = 1
    n = len(list(iterable))
    return itertools.chain(*itertools.imap(lambda x: itertools.combinations(iterable, x), xrange(start, n+1)))


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(itertools.islice(iterable, n))


def tabulate(function, start=0):
    "Return function(0), function(1), ..."
    return itertools.imap(function, itertools.count(start))


def consume(iterator, n):
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        itertools.collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(itertools.islice(iterator, n, n), None)


def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(itertools.islice(iterable, n, None), default)


def quantify(iterable, pred=bool):
    "Count how many times the predicate is true"
    return sum(itertools.imap(pred, iterable))


def padnone(iterable):
    """Returns the sequence elements and then returns None indefinitely.

    Useful for emulating the behavior of the built-in map() function.
    """
    return itertools.chain(iterable, itertools.repeat(None))


def ncycles(iterable, n):
    "Returns the sequence elements n times"
    return itertools.chain.from_iterable(itertools.repeat(tuple(iterable), n))


def dotproduct(vec1, vec2):
    return sum(itertools.imap(itertools.operator.mul, vec1, vec2))


def flatten(listOfLists):
    "Flatten one level of nesting"
    return itertools.chain.from_iterable(listOfLists)


def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.

    Example:  repeatfunc(random.random)
    """
    if times is None:
        return itertools.starmap(func, itertools.repeat(args))
    return itertools.starmap(func, itertools.repeat(args, times))


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)


def grouper_no_fill(iterable, n):  # untested
    sentinal = object()
    for g in grouper(iterable, n, sentinal):
        if g[-1] != sentinal:
            yield g
        else:
            yield g[:g.index(sentinal)]


def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = itertools.cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = itertools.cycle(itertools.slice(nexts, pending))


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))


def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', string.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def unique_justseen(iterable, key=None):
    "List unique elements, preserving order. Remember only the element just seen."
    # unique_justseen('AAAABBBCCDAABBB') --> A B C D A B
    # unique_justseen('ABBCcAD', string.lower) --> A B C A D
    return itertools.imap(next, itertools.imap(itertools.itemgetter(1), itertools.groupby(iterable, key)))


def iter_except(func, exception, first=None):
    """ Call a function repeatedly until an exception is raised.

    Converts a call-until-exception interface to an iterator interface.
    Like __builtin__.iter(func, sentinel) but uses an exception instead
    of a sentinel to end the loop.

    Examples:
        bsddbiter = iter_except(db.next, bsddb.error, db.first)
        heapiter = iter_except(functools.partial(heappop, h), IndexError)
        dictiter = iter_except(d.popitem, KeyError)
        dequeiter = iter_except(d.popleft, IndexError)
        queueiter = iter_except(q.get_nowait, Queue.Empty)
        setiter = iter_except(s.pop, KeyError)

    """
    try:
        if first is not None:
            yield first()
        while 1:
            yield func()
    except exception:
        pass


def random_product(*args, **kwds):
    "Random selection from itertools.product(*args, **kwds)"
    pools = map(tuple, args) * kwds.get('repeat', 1)
    return tuple(itertools.random.choice(pool) for pool in pools)


def random_permutation(iterable, r=None):
    "Random selection from itertools.permutations(iterable, r)"
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(itertools.random.sample(pool, r))


def random_combination(iterable, r):
    "Random selection from itertools.combinations(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(itertools.random.sample(xrange(n), r))
    return tuple(pool[i] for i in indices)


def random_combination_with_replacement(iterable, r):
    "Random selection from itertools.combinations_with_replacement(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(itertools.random.randrange(n) for i in xrange(r))
    return tuple(pool[i] for i in indices)


def tee_lookahead(t, i):
    """Inspect the i-th upcomping value from a tee object
       while leaving the tee object at its current position.

       Raise an IndexError if the underlying iterator doesn't
       have enough values.

    """
    for value in itertools.islice(t.__copy__(), i, None):
        return value
    raise IndexError(i)
