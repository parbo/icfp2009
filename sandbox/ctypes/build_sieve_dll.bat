gcc -c -DBUILD_DLL sieve.c
gcc -shared -o sieve.dll -Wl,--out-implib,sieve.a sieve.o
