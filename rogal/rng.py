import uuid


class AbstractRNG:

    """Abstract Random Number Generator.

    Provides minimal implementation for all methods using only random() output.

    """

    def __init__(self, seed=None):
        self.seed = seed or uuid.uuid4()
        self.rng = self.init_rng(self.seed)

    def init_rng(self, seed):
        raise NotImplementedError()

    def random(self):
        """Return random floats in the half-open interval [0.0, 1.0)."""
        return self.rng.random()

    def randrange(self, start, stop=None):
        """Return random integer from range(start, stop)."""
        if stop is None:
            stop = start
            start = 0
        return int(self.random()*(stop-start))+start

    def randint(self, low, high=None):
        """Return random integer in range [low, high] or [0, low] if high not provieded."""
        if high is None:
            high = low
            low = 0
        return self.randrange(low, high+1)

    def randbool(self):
        """Return random boolean."""
        return self.randint(0, 1)

    def shuffled(self, sequence):
        """Return list with shuffled elements from sequence.

        This is equivalent to sample(sequence, len(sequence), replace=False)

        """
        return self.sample(sequence, len(sequence), replace=False)

    def choice(self, sequence):
        """Return random element from sequence."""
        if not isinstance(sequence, (list, tuple)):
            sequence = list(sequence)
        return sequence[self.randrange(len(sequence))]

    def sample(self, sequence, k, replace=False):
        """Return random k elements from sequence, with or without replacement."""
        if not isinstance(sequence, (list, tuple)):
            sequence = list(sequence)
        sample = []
        for e in range(k):
            r = sequence[self.randrange(len(sequence))]
            if not replace and r in sample:
                continue
            sample.append(r)
        return sample

    def __reduce__(self):
        return (self.__class__, (self.seed, ))


class PyRandomRNG(AbstractRNG):

    """Random Number Generator using random module from python standard module."""

    def init_rng(self, seed):
        import random
        return random.Random(self.seed.int)

    def randrange(self, start, stop=None):
        """Return random integer from range(start, stop)."""
        return self.rng.randrange(start, stop)

    def randint(self, low, high=None):
        """Return random integer in range [low, high] or [0, low] if high not provieded."""
        if high is None:
            high = low
            low = 0
        return self.rng.randint(low, high)

    def choice(self, sequence):
        """Return random element from sequence."""
        if not isinstance(sequence, (list, tuple)):
            sequence = list(sequence)
        return self.rng.choice(sequence)

    def sample(self, sequence, k, replace=False):
        """Return random k elements from sequence, with or without replacement."""
        if not isinstance(sequence, (list, tuple)):
            sequence = list(sequence)
        if replace:
            sample = []
            for e in range(k):
                sample.append(self.randrange(len(sequence)))
        else:
            sample = self.rng.sample(sequence, k)
        return sample


class NumpyRNG(AbstractRNG):

    """Random Number Generator using numpy.random.Generator.

    See: https://numpy.org/doc/stable/reference/random/generator.html

    NOTE: Seems to be slightly slower than PyRandomRNG

    """

    def init_rng(self, seed):
        import numpy.random
        return numpy.random.default_rng(self.seed.int)

    def randint(self, low, high=None):
        """Return random integer in range [low, high] or [0, low] if high not provieded."""
        return self.rng.integers(low, high, endpoint=True)

    def randrange(self, start, stop=None):
        """Return random integer from range(start, stop)."""
        if stop is None:
            stop = start
            start = 0
        return self.rng.integers(start, stop, endpoint=False)

    def shuffled(self, sequence):
        """Return list with shuffled elements from sequence.

        This is equivalent to sample(sequence, len(sequence))

        """
        return self.rng.permutation(list(sequence))

    def choice(self, sequence):
        """Return random element from sequence."""
        if not isinstance(sequence, (list, tuple)):
            sequence = list(sequence)
        #return self.rng.choice(len(sequence))
        # NOTE: np.random.choice() from list on namedtuples returns np.array instead of namedtuple!
        return sequence[self.randrange(len(sequence))]

    def sample(self, sequence, k, replace=False):
        """Return random k elements from sequence, with or without replacement."""
        if not isinstance(sequence, (list, tuple)):
            sequence = list(sequence)
        #return self.rng.choice(sequence, k, replace=replace)
        # NOTE: np.random.choice() from list on namedtuples returns np.array instead of namedtuple!
        return [sequence[i] for i in self.rng.choice(len(sequence), k, replace=replace)]

RNG = PyRandomRNG
# RNG = NumpyRNG


# default instance if we don't care about seeds
rng = RNG()


class RandRange:

    def __init__(self, start, stop=None):
        self.rng = rng
        self.start = start
        self.stop = stop

    def __int__(self):
        return self.rng.randrange(self.start, self.stop)

    def __reduce__(self):
        return (RandRange, self.stop and (self.start, self.stop) or (self.start, ))


class RandInt(RandRange):

    def __init__(self, low, high=None):
        if high is None:
            high = low
            low = 0
        super().__init__(low, high)

    def __reduce__(self):
        return (RandInt, self.high and (self.low, self.high) or (self.low, ))


class RandomTable:

    def __init__(self, rng, *weighted_elements):
        self.rng = rng
        self.elements = []
        for element, weight in weighted_elements:
            self.elements.extend([element,]*weight)

    def choice(self):
        return self.rng.choice(self.elements)

