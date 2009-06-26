#ifndef _SIEVE_H
#define _SIEVE_H

#ifdef BUILD_DLL
// the dll exports
#define EXPORT __declspec(dllexport)
#else
// the exe imports
//#define EXPORT __declspec(dllimport)

// Not intended to be dynamically linked in the C environment.
#define EXPORT extern
#endif
   
// Callback function passing the result of the prime number calculation.
// The callback function must not store a reference to the 'primes' array,
// since it will be freed by the PrimeSieve function when the callback returns.
typedef void (*prime_cb_func_t)(unsigned number_of_primes, unsigned* primes);

// Calculate prime numbers up to (but no including) 'limit', 
// using sieve of Eratosthenes algorithm.
EXPORT void PrimeSieve(unsigned limit, prime_cb_func_t prime_cb);

#endif // _SIEVE_H
