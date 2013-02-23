from math import cos, sin, pi
from random import uniform

from ext import evthandler as eh
import pygame as pg

from conf import conf
from world import World
import gm
from planet import Planet, Sun, Asteroid
from physics import Physics


class Player (Planet):
	def __init__ (self, ident, *args):
		self.img_ident = 'player{0}'.format(ident)
		Planet.__init__(self, *args)


class Level (World):
	def __init__ (self, scheduler, evthandler, n_players = 1):
		World.__init__(self, scheduler, evthandler)
		self.t = 0
		self.scheduler.interp(lambda t: t, self.update_t)
		bg = gm.Colour(((0, 0), conf.RES), (0, 0, 0))
		self.graphics.add(bg)
		bg.layer = conf.GRAPHICS_LAYERS['bg']
		# controls
		js = []
		for i in xrange(n_players):
			j = pg.joystick.Joystick(i)
			j.init()
			js.append(j)
		evthandler.add_event_handlers({
			pg.JOYBUTTONDOWN: self._joycb,
			pg.JOYAXISMOTION: self._joycb
		})

		# sun
		self.phys = Physics()
		p_data = conf.PLAYER_PLANET_DATA
		p_radius = p_data['radius']
		p_sun_dist = p_data['sun dist']
		pad = p_data['edge dist'] + p_sun_dist + p_radius
		s_w, s_h = conf.RES
		assert 2 * pad <= s_w and 2 * pad <= s_h
		sun = Sun(conf.SUN_DENSITY, conf.SUN_RADIUS, (uniform(pad, s_w - pad), uniform(pad, s_h - pad)))
		# players
		angle0 = uniform(0, 2 * pi)
		d_angle = 2 * pi / n_players
		self.players = [Player(i, p_data['density'], p_radius, sun, p_sun_dist, angle0 + i * d_angle) for i in xrange(n_players)]
		# extra planets
		planets = list(self.players)

		self.asteroids = []#Asteroid([300,300],[10,70],1,10)]
		self.phys.gravity_sources = [sun] + planets
		self.entities = self.phys.gravity_sources + self.asteroids
		self.graphics.add(*(e.graphic for e in self.entities))

	def _joycb (self, evt):
		if evt.type == pg.JOYBUTTONDOWN:
			print 'button', evt.button
		else:
			if abs(evt.value) > .5:
				print 'axis', evt.axis

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
			collided_with = ast.collide_with_list(self.entities)
			if collided_with is not None:
				# TODO: collision resolution, this should be done by overriding hit_by_asteroid
				collided_with.hit_by_asteroid(ast)

	def remove_ent(self, ent):
		pass
