from util import Vect

class CollisionEnt(object):
	def __init__ (self, pos, collision_radius):
		self.pos = Vect(pos)
		self.collision_radius = collision_radius

	def collide_with_list (self, collision_list):
		collided_with = []
		for ent in collision_list:
			if ent != self and abs(self.pos - ent.pos)**0.5 < self.collision_radius + self.collision_radius:
				return ent
		return None
	
	def list_collide_with_list (self, collision_list):
		collided_with = []
		for ent in collision_list:
			if ent != self and abs(self.pos - ent.pos)**0.5 < self.collision_radius + self.collision_radius:
				collided_with += ent
		return collided_with

	def hit_by_asteroid (self, asteroid):
		pass
				


