# World constants.
EARTH_RADIUS = 6.357e6 # [m]

class Simulation(object):
    def __init__(self, name=''):
        self.name = name
        self.time = 0
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
        
    @property
    def completed(self):
        return True
    
    @property    
    def porthandles(self):
        return []
        
    def port(self, handle):
        return None
        
def Create():
    return Simulation()

if __name__ == '__main__':
    pass