from math import cos, sin, atan2, pi
from random import uniform

from ext import evthandler as eh
import pygame as pg

from conf import conf
from util import Vect, blank_sfc, position_sfc
from world import World
import gm
from planet import Planet, Sun, Asteroid
from physics import Physics

from player import Player

class Level (World):
	def __init__ (self, scheduler, evthandler, joys):
		World.__init__(self, scheduler, evthandler)
		self._dot_sfc = [conf.GAME.img('dot{0}.png'.format( i ),
			(conf.DOT_RADIUS, conf.DOT_RADIUS)) for i in xrange( 4 )]
		self.t = 0
		self.scheduler.add_timeout(self._update_paths, seconds = conf.PATH_UPDATE_TIME)
		self.scheduler.interp(lambda t: t, self.update_t)
		bg = gm.Colour(((0, 0), conf.RES), (0, 0, 0))
		self.graphics.add(bg)
		bg.layer = conf.GRAPHICS_LAYERS['bg']
		# controls
		# {type: {id: (action, action_mode)}}
		self.controls = controls = {}
		for action, evts in conf.CONTROLS.iteritems():
			if isinstance(evts[0], basestring):
				evts = (evts,)
			for mode, (e_type, e_id) in enumerate(evts):
				controls.setdefault(e_type, {})[e_id] = (action, mode)
		evthandler.add_event_handlers(dict.fromkeys(controls, self._joycb))
		evthandler.add_key_handlers([
			(conf.KEYS_BACK, self.pause, eh.MODE_ONDOWN)
		])

		# sun
		self.phys = Physics()
		p_data = conf.PLAYER_PLANET
		p_radius = p_data['radius']
		p_sun_dist = p_data['sun dist']
		pad = p_data['edge dist'] + p_sun_dist + p_radius
		s_w, s_h = conf.RES
		assert 2 * pad <= s_w and 2 * pad <= s_h
		sun = Sun(conf.SUN_DENSITY, conf.SUN_RADIUS, (uniform(pad, s_w - pad), uniform(pad, s_h - pad)))
		# npps (non player planets)
		# inner planets
		planets = []
		planet_data = conf.INNER_PLANET
		planet_number= planet_data['number']
		planet_max_radius = planet_data['max radius']
		planet_min_radius = planet_data['min radius']
		if planet_number > 0:
			planet_dist = planet_data['min sun dist']
			planet_dist_inc = (planet_data['max sun dist'] - planet_dist)/ planet_number
			for i in xrange(planet_number):
				planets.append(Planet(self, planet_data['density'], uniform(planet_min_radius,planet_max_radius), sun, planet_dist + planet_dist_inc * i, uniform(0,6.29)))
		# outer planets
		planet_data = conf.OUTER_PLANET
		planet_number= planet_data['number']
		planet_max_radius = planet_data['max radius']
		planet_min_radius = planet_data['min radius']
		if planet_number > 0:
			planet_dist = planet_data['min sun dist']
			planet_dist_inc = (planet_data['max sun dist'] - planet_dist)/ planet_number
			for i in xrange(planet_number):
				planets.append(Planet(self, planet_data['density'], uniform(planet_min_radius,planet_max_radius), sun, planet_dist + planet_dist_inc * i, uniform(0,6.29)))

		# players
		angle = uniform(0, 2 * pi)
		d_angle = 2 * pi / len(joys)
		joy_ids = [j.get_id() for j in joys]
		self.players = []
		for i in xrange(4):
			if i in joy_ids:
				self.players.append(Player(i, self, p_data['density'], p_radius, sun, p_sun_dist, angle))
				angle += d_angle
			else:
				self.players.append(None)
		# extra planets
		planets += [p for p in self.players if p is not None]

		asteroids = []
		self.phys.gravity_sources = [sun] + planets
		self.entities = self.phys.gravity_sources + asteroids
		self.graphics.add(*(e.graphic for e in self.entities))

	def _joycb (self, evt):
		p = self.players[evt.joy]
		if p is not None:
			e_ident = evt.button if evt.type == pg.JOYBUTTONDOWN else evt.axis
			controls = self.controls[evt.type]
			if e_ident in controls:
				action, mode = controls[e_ident]
				getattr(p, action)(mode, evt)

	def update_t (self, t):
		phys = self.phys
		dt = t - self.t
		self.t = t
		for e in self.entities:
			e.move(phys, dt)
		self.collision_detection()

	def _update_paths (self):
		sfc = self._dot_sfc
		for i, p in enumerate( self.players ):
			if p is not None:
				p.update_path(sfc[i])
		return True

	def collision_detection(self):
		es = self.entities
		dist = conf.ASTEROID_DESTROY_DIST * 2
		in_bdy = pg.Rect((0, 0), conf.RES).inflate(dist, dist).collidepoint
		for ast in list(es):
			# might have been removed earlier in the loop
			if ast in es:
				if isinstance(ast, Asteroid):
					if not in_bdy(ast.pos):
						self.rm_ast(ast)
					else:
						# Firstly collide with everything
						collided_with = ast.collide_with_list(es)
						try:
							while True:
								ent = next(collided_with)
								if ent.hit_by_asteroid(ast):
									self.rm_ast(ast)
									break
						except StopIteration:
							pass

	def num_players( self ):
		return self.players.count( not None )

	def add_ast (self, ast):
		self.entities.append(ast)
		self.graphics.add(ast.graphic)

	def rm_ast (self, ast):
		self.entities.remove(ast)
		self.graphics.rm(ast.graphic)

	def rm_player (self, player):
		self.entities.remove(player)
		self.graphics.rm(player.graphic)
		self.players[player.player_ident] = None

	def pause (self, *args, **kwargs):
		conf.GAME.start_world(Pause, self.graphics.surface, kwargs.get('player'))


class Pause (World):
	def __init__ (self, scheduler, evthandler, sfc, player = None):
		self.player = player
		World.__init__(self, scheduler, evthandler)
		evthandler.add_event_handlers({pg.JOYBUTTONDOWN: self._joycb})
		evthandler.add_key_handlers([
			(conf.KEYS_BACK, lambda *args: conf.GAME.quit_world(), eh.MODE_ONDOWN),
			(conf.KEYS_QUIT, lambda *args: conf.GAME.quit_world(2), eh.MODE_ONDOWN)
		])
		darken = blank_sfc(conf.RES)
		darken.fill((0, 0, 0, 180))
		darken = gm.Image((0, 0), darken)
		darken.layer = -1
		self.graphics.add(gm.Image((0, 0), sfc), darken)

	def select (self):
		c = (255, 255, 255) if self.player is None else conf.P_COLOURS[self.player]
		text = conf.GAME.render_text('menu', 'Paused\nQ to quit', c, just = 1, line_spacing = conf.MENU_LINE_SPACING)[0]
		sfc = blank_sfc(conf.RES)
		position_sfc(text, sfc)
		img = gm.Image((0, 100), sfc)
		self.graphics.add(img)
		img.layer = -2

	def _joycb (self, evt):
		if (evt.joy == self.player or self.player is None) and evt.button == conf.CONTROLS['pause'][0][1]:
			conf.GAME.quit_world()
