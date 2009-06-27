from simulation import Simulation, EARTH_RADIUS

class TestVm(Simulation):
    def __init__(self, problem, conf):
        Simulation.__init__(self, problem, conf, 'Test simulation')
        self.sx = None
        self.sy = None
        self.vx = None
        self.vy = None
        self.initial_fuel = None
        self.current_fuel = None
        
    def step(self, n=1):
        Simulation.step(self, n)
        self.current_fuel = self.vm.output[1]
        self.sx = self.vm.output[2]
        self.sy = self.vm.output[3]
        self.vx = 0.0
        self.vy = 0.0
        print 'Step:', self.current_fuel, self.sx, self.sy
        
    @property
    def completed(self):
        return self.time > 5000

def Create(problem, conf):
    return TestVm(problem, conf)