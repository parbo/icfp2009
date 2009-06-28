gcc -c -DBUILD_DLL -ffloat-store vm.c
gcc -shared -o vm.dll -Wl,--out-implib,vm.a vm.o
copy vm.dll ..