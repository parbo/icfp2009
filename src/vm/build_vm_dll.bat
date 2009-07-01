gcc -c -DBUILD_DLL -O3 -ffloat-store vm.c
gcc -shared -o vm.dll -Wl,--out-implib,vm.a vm.o
copy vm.dll ..