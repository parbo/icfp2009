from simulation import Simulation, EARTH_RADIUS

class TestSim(Simulation):
    def __init__(self, problem=None, conf=None):
        Simulation.__init__(self, 'Test simulation', problem, conf)
        self.sx = 2 * EARTH_RADIUS
        self.sy = EARTH_RADIUS
        self.vx = 0.0
        self.vy = -1e4
        self.initial_fuel = 5000.0
        self.current_fuel = 5000.0
        
    def step(self, n=1):
        Simulation.step(self, n)
        self.sx += n * self.vx
        self.sy += n * self.vy
        self.vx -= n * 5.0
        self.current_fuel -= n * 1.0
        
    @property
    def completed(self):
        return not (self.current_fuel > 0.0)

def Create(problem, conf):
    return TestSim(problem, conf)