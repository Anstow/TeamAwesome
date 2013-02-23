from math import cos, sin, pi
from random import uniform

from conf import conf
from world import World
import gm
from planet import Planet, Asteroid
from physics import Physics


class Level (World):
	def __init__ (self, scheduler, evthandler, n_players = 2):
		World.__init__(self, scheduler, evthandler)
		self.t = 0
		self.scheduler.interp(lambda t: t, self.update_t)
		bg = gm.Colour(((0, 0), conf.RES), (0, 0, 0))
		self.graphics.add(bg)
		bg.layer = conf.GRAPHICS_LAYERS['bg']

		# sun
		self.phys = Physics()
		p_data = conf.PLAYER_PLANET_DATA
		p_radius = p_data['radius']
		p_sun_dist = p_data['sun dist']
		pad = p_data['edge dist'] + p_sun_dist + p_radius
		s_w, s_h = conf.RES
		assert 2 * pad <= s_w and 2 * pad <= s_h
		sun = Planet(conf.SUN_DENSITY, conf.SUN_RADIUS, (uniform(pad, s_w - pad), uniform(pad, s_h - pad)))
		# players
		angle0 = uniform(0, 2 * pi)
		d_angle = 2 * pi / n_players
		planets = [Planet(p_data['density'], p_radius, sun, p_sun_dist,
		                  angle0 + i * d_angle) for i in xrange(4)]
		# extra planets
		

		self.asteroids = [Asteroid([300,300],[10,70],1,10)]
		self.phys.gravity_sources = [sun] + planets
		self.entities = self.phys.gravity_sources + self.asteroids
		self.graphics.add(*(e.graphic for e in self.entities))

	def update_t (self, t):
		phys = self.phys
		dt = t - self.t
		self.t = t
		for e in self.entities:
			e.move(phys, dt)
		self.collision_detection()

	def collision_detection(self):
		for ast in self.asteroids:
			# Firstly collide with everthing
			# TODO: collide with missiles
			# TODO: collide with force fields
			colided_with=ast.collide_with_list(self.entities)
			if colided_with is not None:
				# TODO: collision resolution, this should be done by overriding hit_by_asteroid
				colided_with.hit_by_asteroid(ast)
				print("coliding")

	def remove_ent(self, ent):
		pass
