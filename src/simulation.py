from vm.vm import VM

# World constants.
EARTH_RADIUS = 6.357e6 # [m]

class Simulation(object):
    def __init__(self, problem, conf, name=''):
        self.name = name
        self.problem = problem
        self.conf = conf
        # VM
        self.vm = VM(problem, conf, 1)
        # State
        self.time = 0
        self.state = State()
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
            self.state = State(self.time, self.vm, self.state)
            slist.append(self.state)
            if self.initial_fuel is None:
                self.initial_fuel = self.state.current_fuel
            self.input()
        self.history.extend(slist)
        return slist
        
    def input(self):
        pass
        
    @property
    def completed(self):
        return self.state.score != 0.0
    
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
        
def Create(problem, conf):
    return Simulation(problem, conf)

if __name__ == '__main__':
    pass