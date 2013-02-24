from math import cos, sin

from conf import conf
from gm import Image
from util import ir, Vect
from physics import GravitySource, GravitySink
from collisions import CollisionEnt


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
			return self.pos.rotate(freq * dt, centre)

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

	def __init__ (self, world, pos, vel, radius = conf.ASTEROID['max radius'], density = conf.ASTEROID['density']):
		self.world = world
		GravitySink.__init__(self, pos, vel, density * radius ** 3, radius)
		self.graphic = Image((ir(pos[0] - radius), ir(pos[1] - radius)), 'planet.png')
		self.graphic = mk_graphic(self)
		position_graphic(self)

	def move (self, phys, t):
		GravitySink.move(self, phys, t)
		x, y = self.pos
		position_graphic(self)

	def hit_by_asteroid (self, ast):
		self.world.rm_ast(self)
		return True

class Shield(CollisionEnt):
	img_ident = 'shield'
	ident = 'shield'

	def __init__ (self, player):
		self.img_ident = 'player{0}'.format(ident)
		self.owned_by = player
		self.angle = 0     # position
		self.size = pi/3   # size / 2 in rad
		self.image = ("image0", "image1", "image2")
		self.tech = 0
		self.thickness = 2
		self.damage = 0

		### radius fudge factors
		self.f = 10
		self.s = 2
		self.world.scheduler.add_timeout(_self.repair, seconds = 1)

	def _repair (self):
		damage = max(damage - 1, 0)

	def strength (self):
		return max(0, self.tech - self.damage)

	def get_radius (self): 
		strength = self.strength()
		radius = 0
		if strength >= 0:
			radius = self.f + strength * self.s
		return radius
			
	#def draw(self, angle):
		#pass
		#strength = self.strength()
		#if strength >= 0:
		#   image = self.image[strength] 
		#   

	def collide_with_list (self, collision_list):
		r = self.radius
		a0 = self.angle
		a1 = clamp_ang(a0 + self.size)
		p = owned_by.pos
		for ent in collision_list:
			ep = ent.pos
			dif = [ ep[0] - p[0], ep[1] - p[1]]
			distance = (dif[0]*dif[0] + dif[1]*dif[1])**.5
			ent_ang = clamp_ang(acos(dif[0] / d_mag))
			if abs(d - r) > self.thickness and ent is not self:
				if ent_ang > a0 and ent_ang < a0 + a1:
					yield ent
