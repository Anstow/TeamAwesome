from math import cos, sin

from conf import conf
from gm import Image
from util import ir, Vect
from physics import GravitySource, GravitySink


class Planet (GravitySource):
	def __init__ (self, density, radius, centre, dist = None,
				  angle = None):
		mass = density * radius ** 3
		if isinstance(centre, Planet):
			pos = (centre.pos[0] + dist * cos(angle),
			       centre.pos[1] + dist * sin(angle))
			freq = float(conf.GRAVITY_CONSTANT * centre.mass) / dist ** 3
			centre = centre.pos

			def get_pos (dt):
				cx, cy = centre
				x, y = self.pos - centre
				c = cos(freq * dt)
				s = sin(freq * dt)
				return Vect(cx + c * x - s * y, cy + s * x + c * y)

			self.get_pos_at_time = get_pos
		else:
			pos = centre
		GravitySource.__init__(self, Vect(pos), mass, radius)
		self.graphic = Image((ir(pos[0] - radius), ir(pos[1] - radius)),
		                     'planet.png')
		self.graphic.resize(2 * radius, 2 * radius)
		self.graphic.layer = conf.GRAPHICS_LAYERS['planet']

	def move (self, phys, dt):
		p = self.get_pos_at_time(dt)
		self.pos = p
		self.graphic.pos = (ir(p[0] - self.collision_radius), ir(p[1] - self.collision_radius))


class Asteroid (GravitySink):
    def __init__ (self, pos, vel, mass = 1, radius = 10):
		GravitySink.__init__(self, pos, vel, mass, radius)
		self.graphic = Image((ir(pos[0] - radius), ir(pos[1] - radius)), 'planet.png')
		self.graphic.resize(2 * radius, 2 * radius)
		self.graphic.layer = conf.GRAPHICS_LAYERS['asteroid']

    def move (self, phys, t):
        GravitySink.move(self, phys, t)
        x, y = self.pos
        self.graphic.pos = (ir(x - self.collision_radius), ir(y - self.collision_radius))
