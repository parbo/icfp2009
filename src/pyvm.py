import struct
import sys
import math

D_OP_ADD = 0x1
D_OP_SUB = 0x2
D_OP_MULT = 0x3
D_OP_DIV = 0x4
D_OP_OUTPUT = 0x5
D_OP_PHI = 0x6
S_OP_NOOP = 0x0
S_OP_CMPZ = 0x1
S_OP_SQRT = 0x2
S_OP_COPY = 0x3
S_OP_INPUT = 0x4
CMPZ_OP_LTZ = 0x0
CMPZ_OP_LEZ = 0x1
CMPZ_OP_EQZ = 0x2
CMPZ_OP_GEZ = 0x3
CMPZ_OP_GTZ = 0x4

ADDRSPACESZ = 16384

def trace(lvl, *args):
    pass
#    if lvl <= dbglvl:
#        print args[0]%args[1:]

class VM(object):
    def __init__(self, filename, conf, dbglvl=0):
        self.debuglevel(dbglvl)
        self.filename = filename
        self.conf = conf
        self.init()
        if not self.load(filename):
            print 'VM: Failed to load', filename
        self.input[0x3e80] = conf

    def debuglevel(self, lvl):
        self.dbglvl = lvl

    def init(self):
        self.status = 0
        self.data = [0.0] * ADDRSPACESZ
        self.instructions = [0] * ADDRSPACESZ
        self.input = [0.0] * ADDRSPACESZ
        self.output = [0.0] * ADDRSPACESZ    

    def load(self, filename):
        f = open(filename, "rb")
        addr = 0
        while addr < ADDRSPACESZ:
            frame = f.read(12)
            if not frame:
                break
            if addr % 2 == 0:
                data, ins = struct.unpack("<dI", frame)
            else:
                ins, data = struct.unpack("<Id", frame)
            self.data[addr] = data
            self.instructions[addr] = ins
            addr += 1
        return 1

    def step(self):
        for pc, ins in enumerate(self.instructions):
            op = ins >> 28
            if (op):
                # D-type instruction
                r1 = (ins >> 14) & 0x3fff;
                r2 = ins & 0x3fff;            
                if op == D_OP_ADD:
                    self.data[pc] = self.data[r1] + self.data[r2]
                    trace(3, "%d D: ADD, %d, %d, %f, %f, %f\n", pc, r1, r2, self.data[r1], self.data[r2], self.data[pc])
                elif op == D_OP_SUB:
                    self.data[pc] = self.data[r1] - self.data[r2]
                    trace(3, "%d D: SUB, %d, %d, %f, %f, %f\n", pc, r1, r2, self.data[r1], self.data[r2], self.data[pc])
                elif op == D_OP_MULT:
                    self.data[pc] = self.data[r1] * self.data[r2]
                    trace(3, "%d D: MULT, %d, %d, %f, %f, %f\n", pc, r1, r2, self.data[r1], self.data[r2], self.data[pc])
                elif op == D_OP_DIV:
                    if self.data[r2] == 0.0:
                        self.data[pc] = 0.0
                    else:
                        self.data[pc] = self.data[r1] / self.data[r2]
                    trace(3, "%d D: DIV, %d, %d, %f, %f, %f\n", pc, r1, r2, self.data[r1], self.data[r2], self.data[pc])
                elif op == D_OP_OUTPUT:
                    self.output[r1] = self.data[r2]
                    trace(3, "%d D: OUTPUT, %d, %d, %f, %f, %f\n", pc, r1, r2, self.data[r1], self.data[r2], self.output[r1])
                elif op == D_OP_PHI:
                    self.data[pc] = self.data[r1] if self.status else self.data[r2]
                    trace(3, "%d D: PHI, %d, %d, %f, %f, %f, %d\n", pc, r1, r2, self.data[r1], self.data[r2], self.data[pc], self.status)
            else:
                # S-type instruction
                imm = (ins >> 21) & 0x7;
                r1 = ins & 0x3fff;
                op = (ins >> 24) & 0xf;
                if op == S_OP_NOOP:
                    trace(3, "%d S: NOOP, %d, %d, %f, %f\n", pc, imm, r1, self.data[r1], self.data[pc])
                    pass
                elif op == S_OP_CMPZ:
                    if imm == CMPZ_OP_LTZ:
                        self.status = 1 if self.data[r1] < -1e-300 else 0
                        trace(3, "%d S: CMPZ <, %d, %d, %f, %f, %d\n", pc, imm, r1, self.data[r1], self.data[pc], self.status)
                    elif imm == CMPZ_OP_LEZ:
                        self.status = 1 if self.data[r1] <= 0.0 else 0
                        trace(3, "%d S: CMPZ <=, %d, %d, %f, %f, %d\n", pc, imm, r1, self.data[r1], self.data[pc], self.status)
                    elif imm == CMPZ_OP_EQZ:
                        self.status = 1 if self.data[r1] == 0.0 else 0
                        trace(3, "%d S: CMPZ ==, %d, %d, %f, %f, %d\n", pc, imm, r1, self.data[r1], self.data[pc], self.status)
                    elif imm == CMPZ_OP_GEZ:
                        self.status = 1 if self.data[r1] >= 1e-300 else 0
                        trace(3, "%d S: CMPZ >=, %d, %d, %f, %f, %d\n", pc, imm, r1, self.data[r1], self.data[pc], self.status)
                    elif imm == CMPZ_OP_GTZ:
                        self.status = 1 if self.data[r1] > 0.0 else 0
                        trace(3, "%d S: CMPZ >, %d, %d, %f, %f, %d\n", pc, imm, r1, self.data[r1], self.data[pc], self.status)
                elif op == S_OP_SQRT:
                    self.data[pc] = abs(math.sqrt(self.data[r1]))
                    trace(3, "%d S: SQRT, %d, %d, %f, %f\n", pc, imm, r1, self.data[r1], self.data[pc])
                elif op == S_OP_COPY:
                    self.data[pc] = self.data[r1]
                    trace(3, "%d S: COPY, %d, %d, %f, %f\n", pc, imm, r1, self.data[r1], self.data[pc])
                elif op == S_OP_INPUT:
                    self.data[pc] = float(self.input[r1])
                    trace(3, "%d S: INPUT, %d, %d, %f, %f\n", pc, imm, r1, self.data[r1], self.data[pc])
