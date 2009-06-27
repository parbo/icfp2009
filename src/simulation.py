import math
from vm.vm import VM
from submission import Submission

# World constants.
EARTH_RADIUS = 6.357e6 # [m]

class Simulation(object):
    def __init__(self, problem, conf, name=''):
        self.name = name
        self.problem = problem
        self.conf = conf
        self.submission = Submission(7, conf)
        self.submission.add(0, [(0x3e80, conf)])
        # VM
        self.vm = VM(problem, conf, 1)
        # State
        self.time = 0
        self.state = self.create_state()
        self.history = [self.state]
        # Fuel
        self.initial_fuel = None
        # Default world size.
        self.world_size = (2.2 * EARTH_RADIUS, 2.2 * EARTH_RADIUS)
        
    def step(self, n=1):
        slist = []
        for t in range(n):
            self.time += 1
            self.vm.step()
            if self.completed:
                break
            self.state = self.create_state(self.time, self.vm, self.state)
            slist.append(self.state)
            if self.initial_fuel is None:
                self.initial_fuel = self.state.current_fuel
            dvx = self.vm.input[2]
            dvy = self.vm.input[3]
            self.input()
            pv = []
            if dvx != self.vm.input[2]:
                pv.append((2, self.vm.input[2])) 
            if dvy != self.vm.input[3]:
                pv.append((3, self.vm.input[3])) 
            if pv and not self.completed:
                self.submission.add(self.time, pv)
                
        self.history.extend(slist)
        return slist
        
    def input(self):
        pass
        
    @property
    def completed(self):
        return self.state.score != 0.0
        
    def create_state(self, time=0, vm=None, previous=None):
        return State(time, vm, previous)
    
    @property    
    def porthandles(self):
        return []
        
    def port(self, handle):
        return None
        
class State(object):
    def __init__(self, time=0, vm=None, previous=None):
        self.time = time
        self.score = 0.0
        # Satellite position
        self.sx = None
        self.sy = None
        # Satellite velocity
        self.vx = None
        self.vy = None
        # Fuel
        self.current_fuel = None
        if (time > 0) and (vm is not None):
            self.score = vm.output[0]
            self.current_fuel = vm.output[1]
            self.sx = vm.output[2]
            self.sy = vm.output[3]
            if previous is not None:
                try:
                    self.vx = self.sx - previous.sx
                    self.vy = self.sy - previous.sy
                except TypeError:
                    pass
        # Other satellites
        self.satellites = self.get_satellites(vm, previous)
                    
    def __str__(self):
        s = []
        s.append('time:  ' + str(self.time))
        s.append('score: ' + str(self.score))
        s.append('fuel:  ' + str(self.current_fuel))
        s.append('sx:    ' + str(self.sx))
        s.append('sy:    ' + str(self.sy))
        s.append('vx:    ' + str(self.vx))
        s.append('vy:    ' + str(self.vy))
        return '\n'.join(s)
        
    def number_of_satellites(self):
        return 0
        
    def satellite_ports(self, satellite_ix):
        return None
        
    def get_satellites(self, vm, previous):
        s = []
        for ix in range(self.number_of_satellites()):
            xport, yport = self.satellite_ports(ix)
            s.append(Satellite(self, xport, yport, previous))
        return s
        
class MeetAndGreetState(State):
    def __init__(self, time=0, vm=None, previous=None):
        State.__init__(self, time, vm, previous)
        
    def number_of_satellites(self):
        return 1
        
    def satellite_ports(self, satellite_ix):
        return (4, 5)
        
def Satellite(object):
    def __init__(self, ref_sat, xport, yport, previous):
        self.rx = None
        self.ry = None
        self.sx = None
        self.sy = None
        self.radius = None
        self.vx = None
        self.vy = None
        if (time > 0) and (vm is not None):
            self.rx = vm.output[xport]
            self.ry = vm.output[yport]
            self.sx = ref_sat.sx - self.rx
            self.sy = ref_sat.sy - self.ry
            self.radius = math.sqrt(self.sx ** 2, self.sy ** 2)
            try:
                self.vx = self.sx - previous.sx
                self.vy = self.sy - previous.sy
            except TypeError:
                pass
        
def Create(problem, conf):
    return Simulation(problem, conf)

if __name__ == '__main__':
    pass
