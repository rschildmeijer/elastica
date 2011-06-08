from random import Random

""" Initial version by Raymond Hettinger (@raymondh)
(http://code.activestate.com/recipes/577684-bloom-filter/) """
class BloomFilter:
    """Space efficient, probabilistic set membership tester.
       Has no False Negatives but allows a rare False Positive."""

    # http://en.wikipedia.org/wiki/Bloom_filter

    def __init__(self, num_bytes, num_probes, iterable=()):
        self._array = bytearray(num_bytes)
        self._num_probes = num_probes
        self._num_bins = num_bytes * 8
        self.update(iterable)

    def get_probes(self, key):
        random = Random(key).random
        return (int(random() * self._num_bins) for _ in range(self._num_probes))

    def update(self, keys):
        for key in keys:
            for i in self.get_probes(key):
                self._array[i // 8] |= 2 ** (i % 8)

    def __contains__(self, key):
        return all(self._array[i // 8] & (2 ** (i % 8)) for i in self.get_probes(key))
  