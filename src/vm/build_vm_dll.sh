#!/bin/sh
gcc -Wall -fPIC -g -c vm.c
gcc -shared -Wl,-soname,libvm.so.1 -o libvm.so.1.0.1 vm.o -lc
sudo cp libvm.so.1.0.1 /usr/lib
sudo ldconfig -n /usr/lib