import uuid

from numpy import random


class NumpyRNG:

    """Random Number Generator using numpy.random.Generator.

    See: https://numpy.org/doc/stable/reference/random/generator.html

    """

    def __init__(self, seed=None):
        self.seed = seed or uuid.uuid4()
        self.rng = random.default_rng(self.seed.int)

    def random(self):
        """Return random floats in the half-open interval [0.0, 1.0)."""
        return self.rng.random()

    def randbool(self):
        """Return random boolean."""
        return self.rng.integers(1, endpoint=True)

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
        return sequence[self.rng.choice(len(sequence))]

    def sample(self, sequence, k, replace=False):
        """Return random k elements from sequence, with or without replacement."""
        if not isinstance(sequence, (list, tuple)):
            sequence = list(sequence)
        #return self.rng.choice(sequence, k, replace=replace)
        return [sequence[i] for i in self.rng.choice(len(sequence), k, replace=replace)]

RNG = NumpyRNG


class RandomTable:

    def __init__(self, rng, *weighted_elements):
        self.rng = rng
        self.elements = []
        for element, weight in weighted_elements:
            self.elements.extend([element,]*weight)

    def choice(self):
        return self.rng.choice(self.elements)

