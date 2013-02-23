from util import Vect

class CollisionEnt(object):
	def __init__ (self, pos, collision_radius):
		self.pos = Vect(pos)
		self.collision_radius = collision_radius
	
	def collide_with_list (self, collision_list):
		r = self.collision_radius
		p = self.pos
		for ent in collision_list:
			ep = ent.pos
			dx = p[0] - ep[0]
			dy = p[1] - ep[1]
			if ent is not self and (dx * dx + dy * dy) ** .5 < r + ent.collision_radius:
				yield ent

	def hit_by_asteroid (self, asteroid):
		pass
