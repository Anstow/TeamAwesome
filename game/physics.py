from conf import conf

class GravitySource(object):
	def __init__ (self, pos, mass):
		self.pos = list(pos)
		self.mass = mass
	
	def get_pos_at_time(time):
		return self.pos

class Physics(object)
	def __init__ (self):
		self.gravity_sources = []
		self.asteroids = []

	def calculate_acceleration_offset(self, pos, time):
		accel = [0,0]
		for g in self.gravity_sources:
			tmp_pos = g.get_pos_at_time(time)
			dist_2 = (pos[0] - temp_pos[0])**2 + (pos[1] - temp_pos[1])**2
			assert dist_2 != 0
			accel[0] += conf.GRAVITY_CONSTANT * g.mass * float(tmp_pos[0]-pos[0])/(dist_2**1.5)
			accel[1] += conf.GRAVITY_CONSTANT * g.mass * float(tmp_pos[1]-pos[1])/(dist_2**1.5)
		return accel

	def predict_future_positions(self, g_src, no_positions, position_time_offset):
		assert position_time_offset >= conf.DEFAULT_TIME_OFFSET
		current_pos = g_src.pos

