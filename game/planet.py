from math import cos, sin
from random import randrange

from conf import conf
from gm import Graphic
from util import ir, Vect
from physics import GravitySource, GravitySink


def mk_graphic (obj):
	graphic = Graphic(obj.img_ident + '.png',
					  layer = conf.GRAPHICS_LAYERS[obj.ident])
	w = graphic.w
	offset = conf.IMG_OFFSETS[obj.img_ident]
	scale = 2 * float(obj.collision_radius) / (w - 2 * offset)
	graphic.rescale_both(scale)
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
		if self.img_ident == 'planet':
			self.img_ident += str(randrange(3))
		self.world = world
		pos = (centre.pos[0] + dist * cos(angle),
				centre.pos[1] + dist * sin(angle))
		freq = float(conf.GRAVITY_CONSTANT * centre.mass) / dist ** 3
		centre = centre.pos

		def get_pos (dt):
			x, y = self.pos
			cx, cy = centre
			x -= cx
			y -= cy
			angle = freq * dt
			c = cos(angle)
			s = sin(angle)
			return (cx + c * x - s * y, cy + s * x + c * y)

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
	img_ident = 'asteroid'

	def __init__ (self, world, pos, vel, radius = conf.ASTEROID['max radius'], density = conf.ASTEROID['density']):
		self.world = world
		GravitySink.__init__(self, pos, vel, density * radius ** 3, radius)
		self.graphic = Graphic('asteroid.png',
							   (ir(pos[0] - radius), ir(pos[1] - radius)))
		self.graphic = mk_graphic(self)
		position_graphic(self)

	def move (self, phys, t):
		GravitySink.move(self, phys, t)
		x, y = self.pos
		position_graphic(self)

	def hit_by_asteroid (self, ast):
		self.world.rm_ast(self)
		return True
