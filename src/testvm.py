from simulation import Simulation, EARTH_RADIUS

class TestVm(Simulation):
    def __init__(self, problem, conf):
        Simulation.__init__(self, problem, conf, 'Test simulation')
        
    @property
    def completed(self):
        return self.time > 5000

def Create(problem, conf):
    return TestVm(problem, conf)