from simulation import Simulation
import struct


class SubmissionSim(Simulation):
    def __init__(self, problem=None, conf=None):
        Simulation.__init__(self, problem, conf, 'Hohmann transfer simulation')   
        self.actions = {}
        self.submission_text()
 
    def submission_text(self):
        f = open("1001.osf", 'rb')
        magic, team, scenario = struct.unpack('<III', f.read(12))
        print 'Team:     %5d' % team
        print 'Scenario: %5d' % scenario
        print
        frame = 0
        time, count = struct.unpack('<II', f.read(8))
        while count > 0:
            pv = []
            print 'Frame: %d, t=%d' % (frame, time)
            for port in range(count):
                address, value = struct.unpack('<Id', f.read(12))
                pv.append((address, value))
                print 'Port %d: %f' % (address, value)
            print
            self.actions[time] = pv
            time, count = struct.unpack('<II', f.read(8))
            frame += 1
        f.close()
        print self.actions

    def input(self):
        self.vm.input[2] = 0.0
        self.vm.input[3] = 0.0
        try:
            pv = self.actions[self.state.time]
            for a, v in pv:
                self.vm.input[a] = v
        except KeyError:            
            pass

def Create(problem, conf):
    return SubmissionSim(problem, conf)
