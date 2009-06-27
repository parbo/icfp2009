import ctypes
import sys

class VMLibMissing(Exception):
    pass

class VMMemory(object):
    def __init__(self, read, write):
        self._read = read
        self._write = write

    def __getitem__(self, key):
        return self._read(key)

    def __setitem__(self, key, value):
        self._write(key, value)

class VM(object):
    def __init__(self, filename, conf, dbglvl=0):
        try:
            self._vm = ctypes.cdll.vm
        except OSError:
            try:
                self._vm = ctypes.cdll.LoadLibrary("libvm.so.1")
            except OSError:        
                raise VMLibMissing

        self._vm.readoutput.restype = ctypes.c_double
        self._vm.readoutput.argtypes = [ctypes.c_uint]
        self._vm.readinput.restype = ctypes.c_double
        self._vm.readinput.argtypes = [ctypes.c_uint]
        self._vm.writeinput.argtypes = [ctypes.c_uint, ctypes.c_double]

        self.debuglevel(dbglvl)
        self.input = VMMemory(self._vm.readinput, self._vm.writeinput)
        self.output = VMMemory(self._vm.readoutput, None)        
        self.filename = filename
        self.conf = conf
        self._vm.init()
        if not self._vm.load(filename):
            print 'VM: Failed to load', filename
        self.input[0x3e80] = conf

    def step(self):
        self._vm.timestep()    

    def debuglevel(self, lvl):
        self._vm.debuglevel(lvl)

def run(filename, conf):
    vm = VM(filename, conf)

    vm.debuglevel(1)

    ctr = 0
    vm.input[0x3e80] = conf
    print vm.input[0x3e80]
    while vm.output[0] != -1.0:
        ctr += 1
#        print vm.output[0], vm.output[1], vm.output[2], vm.output[3], vm.output[4]
        vm.step()
#    print vm.output[0], vm.output[1], vm.output[2], vm.output[3], vm.output[4]
    print ctr, "steps were run"

if __name__=="__main__":
    run(sys.argv[1], int(sys.argv[2]))
