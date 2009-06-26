#include <math.h>
#include <string.h>
#include "sieve.h"

#define MAX_INT_SQRT 65536

// Maximum number of primes below 'limit'.
// Ref: http://mathworld.wolfram.com/PrimeCountingFunction.html (#5)
static unsigned PrimeMaxCount(unsigned limit)
{
    return (unsigned)(1.25506 * limit / log(limit));
}

void PrimeSieve(unsigned limit, prime_cb_func_t prime_cb)
{
    unsigned max_primes = PrimeMaxCount(limit);
    
    // Reserve enough space to store all primes. Memory initialized to zero by calloc().
    unsigned* primes = (unsigned*)calloc(max_primes, sizeof(unsigned));
    
    // Create flag array.
    unsigned char* is_prime = (unsigned char*)malloc(limit);
    
    unsigned found_primes = 0;
    unsigned i = 2;
    unsigned j = 0;
    
    if(primes && is_prime)
    {
        memset(is_prime, 1, limit);
        is_prime[0] = 0;
        is_prime[1] = 0;
        
        while(i < limit)
        {
            if(is_prime[i])
            {
                primes[found_primes] = i;
                ++found_primes;
                
                if(i < MAX_INT_SQRT)
                {
                    j = i * i;
                    
                    while(j < limit)
                    {
                        is_prime[j] = 0;
                        j += i;
                    }
                }
            }
            
            ++i;
        }
        
        if(prime_cb)
        {
            prime_cb(found_primes, primes);
        }
    }
    
    free(is_prime);
    free(primes);
}
