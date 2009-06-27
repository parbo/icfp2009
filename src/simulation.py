from vm.vm import VM

# World constants.
EARTH_RADIUS = 6.357e6 # [m]

class Simulation(object):
    def __init__(self, problem, conf, name=''):
        self.name = name
        self.problem = problem
        self.conf = conf
        self.time = 0
        # VM
        self.vm = VM(problem, conf, 1)
        # Satellite position
        self.sx = None
        self.sy = None
        # Satellite velocity
        self.vx = None
        self.vy = None
        # Fuel
        self.initial_fuel = None
        self.current_fuel = None
        
    def step(self, n):
        self.time += n
        for t in range(n):
            self.vm.step()
        
    @property
    def completed(self):
        return True
    
    @property    
    def porthandles(self):
        return []
        
    def port(self, handle):
        return None
        
def Create(problem, conf):
    return Simulation(problem, conf)

if __name__ == '__main__':
    pass