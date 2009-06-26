#!/usr/bin/env python

import ctypes
import sys


def run(filename, conf):
    try:
        vm = ctypes.cdll.vm
    except:
        print "No Windows lib found, trying Linux"
        try:
            vm = ctypes.cdll.LoadLibrary("libvm.so.1")
        except:        
            print "No Linux lib found"

    vm.readoutput.restype = ctypes.c_double
    vm.readoutput.argtypes = [ctypes.c_uint]
    vm.readinput.restype = ctypes.c_double
    vm.readinput.argtypes = [ctypes.c_uint]
    vm.writeinput.argtypes = [ctypes.c_uint, ctypes.c_double]

    vm.init()
    vm.load(filename)
    ctr = 0
    vm.writeinput(0x3e80, conf)
    print vm.readinput(0x3e80)
    while vm.readoutput(0) != -1.0:
        ctr += 1
        print vm.readoutput(0), vm.readoutput(1), vm.readoutput(2), vm.readoutput(3), vm.readoutput(4)
        vm.timestep()
    print vm.readoutput(0), vm.readoutput(1), vm.readoutput(2), vm.readoutput(3), vm.readoutput(4)
    print ctr, "steps were run"

if __name__=="__main__":
    run(sys.argv[1], int(sys.argv[2]))
