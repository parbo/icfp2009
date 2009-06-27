import struct

#    byte      value
#       0 0xCAFEBABE
#       4    TeamID
#       8   ScenarioID
#      12   TimeStep0
#      16 Count (e.g. k)
#      20     Addri
#      24     Valuei
#      28
#                .
#                .
#                .
# 20+k*12   TimeStep1
# 24+k*12     Count
#                .
#                .
#                .

class Submission(object):
    HEADERFMT = "<III"
    STEPHDRFMT = "<II"
    PORTFMT = "<Id"
    
    def __init__(self, team, scenario):
        self._header = struct.pack(Submission.HEADERFMT, 0xCAFEBABE, team, scenario)
        self._steps = []

    def add(self, time, portvalues):
        self._steps.append((time, portvalues))
        self._steps.sort()


    def __str__(self):
        tmp = [self._header]        
        for i, s in enumerate(self._steps):
            t, pvs = s
            tmp.append(struct.pack(Submission.STEPHDRFMT, t, len(pvs)))
            for p, v in pvs:
                tmp.append(struct.pack(Submission.PORTFMT, p, v))
        return "".join(tmp)

if __name__=="__main__":
    s = Submission(7, 1001)
    s.add(0, [(0, 0)])
    s.add(1, [(42, 3), (11,7)])
    s.add(2, [(12, 5), (45, 3.14), (7, 2.78)])
    s.add(3, [])
    print s

