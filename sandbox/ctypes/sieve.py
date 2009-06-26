import ctypes
import time

class Prime(object):
    def __init__(self, limit):
        self.limit = limit
        sieve = ctypes.cdll.sieve
        # Create function type that matches signature of PrimeSieve().
        CBFUNC = ctypes.CFUNCTYPE(None, ctypes.c_uint, ctypes.POINTER(ctypes.c_uint))
        # Create callback function object.
        cbfunc=CBFUNC(self._primes_cb)
        sieve.PrimeSieve(limit + 1, cbfunc)
        return
        
    def _primes_cb(self, number_of_primes, primes):
        numbers = number_of_primes * [None]
        for i in xrange(number_of_primes):
            numbers[i] = int(primes[i])
        self.numbers = numbers
        return None

t = time.clock()
prime = Prime(100)
print prime.numbers[:30]
print
print '%.3fs' % (time.clock() - t)