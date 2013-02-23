from math import cos, sin

from conf import conf
from gm import Image
from util import ir
from physics import GravitySource

class Planet (GravitySource):
    def __init__ (self, world, density, centre, radius, angle):
        mass = density * radius ** 3
        pos = (centre[0] + radius * cos(angle),
               centre[1] + radius * sin(angle))
        freq = (conf.GRAVITY_CONSTANT * mass / radius ** 3)
        get_pos = lambda t: (pos[0] + radius * cos(freq * t + angle),
                             pos[1] + radius * sin(freq * t + angle))
        world.scheduler.interp(get_pos, self.set_pos, multi_arg = True)
        self.get_pos_at_time = get_pos
        GravitySource.__init__(self, list(pos), mass)
        self.radius = radius
        first_pos = get_pos(0)
        self.graphic = Image((ir(first_pos[0] - radius),
                             ir(first_pos[1] - radius)), 'planet.png')
        self.graphic.resize(radius, radius)
        self.graphic.layer = conf.GRAPHICS_LAYERS['planet']

    def set_pos (self, x, y):
        self.pos = (x, y)
        self.graphic.pos = (ir(x - self.radius), ir(y - self.radius))
