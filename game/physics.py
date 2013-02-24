from conf import conf
from util import Vect
from collisions import CollisionEnt

class GravitySource(CollisionEnt):
	def __init__ (self, pos, mass, collision_radius):
		CollisionEnt.__init__(self, pos, collision_radius)
		self.mass = mass
	
	def get_pos_at_time(self, time_offset):
		return self.pos

class GravitySink(CollisionEnt):
	def __init__ (self, pos, vel, mass, collision_radius):
		CollisionEnt.__init__(self, pos, collision_radius)
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
		accel = Vect(0, 0)
		grav = conf.GRAVITY_CONSTANT
		for g in self.gravity_sources:
			tmp_pos = g.get_pos_at_time(time)
			dp = tmp_pos - pos
			dist_2 = abs(dp)
			assert dist_2 != 0
			accel += dp * (grav * g.mass / (dist_2 ** 1.5))
		return accel

	def predict_future_positions(self, g_sink, n_ps, n_steps):
		"""Predicts the future positions.

predict_future_positions(g_sink, n_ps, pos_dt)

g_sink: The sink to predict the future of; can also be
		(initial_position, initial_velocity)
n_ps: The number of positions to compute
n_steps: the multiple of conf.DEFAULT_TIME_OFFSET to space out positions by

"""
		assert pos_dt >= conf.DEFAULT_TIME_OFFSET
		ps = []
		if isinstance(g_sink, GravitySink):
			p = g_sink.pos
			v = g_sink.vel
		else:
			p, v = g_sink
		calc_dt = conf.DEFAULT_TIME_OFFSET
		da = self.calculate_accel_offset
		t = 0
		for n_done in xrange(n_ps):
			for i in xrange(n_steps):
				acc_t = calc_dt * da(p, t)
				p += calc_dt * (v + .5 * acc_t)
				v += acc_t
				t += calc_dt
			ps.append(Vect(p))
		return ps
