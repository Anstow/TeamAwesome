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
