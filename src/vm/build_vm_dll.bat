gcc -c -DBUILD_DLL vm.c
gcc -shared -o vm.dll -Wl,--out-implib,vm.a vm.o
