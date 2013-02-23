from conf import conf
from pygame import Rect

class Vect(list):
	def __init__ (self, *args):
		if len(args) >= 2:
			v = args[:2]
		else:
			v = args[0]
		list.__init__(self, v)

	def __abs__(self):
		return self[0]**2 + self[1]**2

	def __add__ (self, v):
		return Vect(self[0] + v[0], self[1] + v[1])

	def __sub__ (self, v):
		return Vect(self[0] - v[0], self[1] - v[1])

	def __iadd__ (self, v):
		self[0] += v[0]
		self[1] += v[1]
		return self

	def __isub__ (self, v):
		self[0] -= v[0]
		self[1] -= v[1]
		return self

	def __mul__ (self, c):
		return Vect(c*self[0], c*self[1])

	__rmul__ = __mul__

	def __div__ (self, c):
		assert(c != 0)
		tmpC = 1./c
		return Vect(tmpC*self[0], tmpC*self[1])

class CollisionEnt(object):
	def __init__ (self, pos, collision_radius):

class GravitySource(CollisionEnt):
	def __init__ (self, pos, mass, collision_radius):
		CollisionEnt.__init__(pos, collision_radius)
		self.mass = mass
	
	def get_pos_at_time(time_offset):
		return self.pos

class GravitySink(CollisionEnt):
	def __init__ (self, pos, vel, mass, collision_radius):
		CollisionEnt.__init__(pos, collision_radius)
		self.vel = Vect(vel)
		self.mass = mass

	def move(self, phys, time_offset):
		tmp_acc_t = time_offset * phys.calculate_accel_offset(self.pos, time_offset)
		self.pos += time_offset * (self.vel + 0.5 * tmp_acc_t)
		self.vel += tmp_acc_t

class Physics(object):
	def __init__ (self):
		self.gravity_sources = []

	def calculate_accel_offset(self, pos, time):
		accel = Vect(0,0)
		for g in self.gravity_sources:
			tmp_pos = g.get_pos_at_time(time)
			dist_2 = abs(tmp_pos - pos)
			assert dist_2 != 0
			accel += (tmp_pos-pos) * (conf.GRAVITY_CONSTANT * g.mass /(dist_2**1.5))
		return accel

	def predict_future_positions(self, g_sink, no_positions, position_time_offset):
		"""Predicts the future positions.

predict_future_positions(g_sink, no_positions, position_time_offset)

g_sink: The sink to predict the future of
no_positions: The number of positions to compute
position_time_offset: The time offset between positions, this will work better
                      if its a multiple of conf.DEFAULT_TIME_OFFSET

"""
		assert position_time_offset >= conf.DEFAULT_TIME_OFFSET
		pos_list = []
		current_pos = g_sink.vel
		current_vel = g_sink.vel
		current_time = 0
		current_n=0
		while current_n<no_positions:
			while current_time<no_positions*position_time_offset:
				tmp_acc_t = conf.DEFAULT_TIME_OFFSET * phys.calculate_accel_offset(current_pos, time_offset)
				current_pos += conf.DEFAULT_TIME_OFFSET * (vel + 0.5 * tmp_acc_t)
				self.vel += tmp_acc_t
				current_time+=conf.DEFAULT_TIME_OFFSET
			current_n+=1
			pos_list += current_pos
		return pos_list
