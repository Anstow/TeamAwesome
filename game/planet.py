from math import cos, sin

from conf import conf
from gm import Image
from util import ir, Vect
from physics import GravitySource, GravitySink


def mk_graphic (obj):
	graphic = Image((0, 0), obj.img_ident + '.png')
	w = graphic.w
	offset = conf.IMG_OFFSETS[obj.img_ident]
	scale = 2 * float(obj.collision_radius) / (w - 2 * offset)
	graphic.rescale(scale, scale)
	graphic.layer = conf.GRAPHICS_LAYERS[obj.ident]
	obj.img_offset = ir(scale * offset)
	return graphic


def position_graphic (obj):
	o = obj.img_offset
	p = obj.pos
	r = obj.collision_radius
	obj.graphic.pos = (ir(p[0] - r - o), ir(p[1] - r - o))


class Planet (GravitySource):
	img_ident = ident = 'planet'

	def __init__ (self, world, density, radius, centre, dist, angle):
		self.world = world
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
		GravitySource.__init__(self, pos, density * radius ** 3, radius)
		self.graphic = mk_graphic(self)
		position_graphic(self)

	def move (self, phys, dt):
		p = self.get_pos_at_time(dt)
		self.pos = p
		position_graphic(self)


class Sun (GravitySource):
	img_ident = ident = 'sun'

	def __init__ (self, density, radius, pos):
		GravitySource.__init__(self, pos, density * radius ** 3, radius)
		self.graphic = mk_graphic(self)
		position_graphic(self)

	def move (self, phys, dt):
		pass


class Asteroid (GravitySink):
	ident = 'asteroid'
	img_ident = 'planet'

	def __init__ (self, pos, vel, mass = 1, radius = 10):
		GravitySink.__init__(self, pos, vel, mass, radius)
		self.graphic = Image((ir(pos[0] - radius), ir(pos[1] - radius)), 'planet.png')
		self.graphic = mk_graphic(self)
		position_graphic(self)

	def move (self, phys, t):
		GravitySink.move(self, phys, t)
		x, y = self.pos
		position_graphic(self)
