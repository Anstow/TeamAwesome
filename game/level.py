from math import cos, sin, atan2, pi
from random import uniform

from ext import evthandler as eh
import pygame as pg

from conf import conf
from util import Vect
from world import World
import gm
from planet import Planet, Sun, Asteroid
from physics import Physics


class Dot (gm.Image):
	def __init__ (self, pos, sfc):
		gm.Image.__init__(self, pos, sfc)
		r = pg.Rect(self.rect)
		r.center = pos
		self.rect = r
		self.layer = conf.GRAPHICS_LAYERS['dot']


class Player (Planet):
	def __init__ (self, ident, *args):
		self.img_ident = 'player{0}'.format(ident)
		Planet.__init__(self, *args)
		self.launch_speed = conf.ASTEROID_LAUNCH_SPEED
		self._since_last_launch = conf.ASTEROID_LAUNCH_GAP
		self.n_dots = conf.PLAYER_N_DOTS
		self.aiming = [[0, 0], [0, 0]] # (defensive, offensive) (x, y)
		self.aiming_angle = [0, 0]
		self._fire_last = [0, 0] # (defensive, offensive) - since fire are axes
		self._dots = []
		self._aim_mag = 0

	def aim (self, mode, evt):
		action = mode >= 2
		v = self.aiming[action]
		v = list(v)
		v[mode % 2] = evt.value
		x, y = v
		if (x * x + y * y) ** .5 >= conf.AIM_THRESHOLD:
			self.aiming[action] = v
			self.aiming_angle[action] = atan2(y, x)
			self._aim_mag = (x * x + y * y) ** .5

	def _init_ast (self):
		angle = self.aiming_angle[1]
		pos = self.pos + Vect(conf.ASTEROID_LAUNCH_DIST, 0).rotate(angle)
		vel = (self.launch_speed * cos(angle), self.launch_speed * sin(angle))
		return (pos, vel)

	def fire (self, mode, evt):
		last = self._fire_last[mode]
		now = evt.value
		if last < conf.TRIGGER_THRESHOLD and now >= conf.TRIGGER_THRESHOLD:
			if mode == 1 and self._since_last_launch >= conf.ASTEROID_LAUNCH_GAP:
				# fire asteroid
				pos, vel = self._init_ast()
				self.world.add_ast(Asteroid(self.world, pos, vel))
				self._since_last_launch = 0
		self._fire_last[mode] = now

	def move (self, phys, dt):
		Planet.move(self, phys, dt)
		self._since_last_launch += dt
		angle = self.aiming_angle[1]

	def update_path (self, dot_sfc):
		# update future path
		self.world.graphics.rm(*self._dots)
		self._dots = [Dot(p, dot_sfc) for p in self.world.phys.predict_future_positions(self._init_ast(), self.n_dots, conf.PLAYER_DOT_DISTANCE)]
		self.world.graphics.add(*self._dots)


class Level (World):
	def __init__ (self, scheduler, evthandler, n_players = 1):
		World.__init__(self, scheduler, evthandler)
		self._dot_sfc = conf.GAME.img('dot.png', (conf.DOT_RADIUS, conf.DOT_RADIUS))
		self.t = 0
		self.scheduler.add_timeout(self._update_paths, seconds = conf.PATH_UPDATE_TIME)
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
		# {type: {id: (action, action_mode)}}
		self.controls = controls = {}
		for action, evts in conf.CONTROLS.iteritems():
			if isinstance(evts[0], basestring):
				evts = (evts,)
			for mode, (e_type, e_id) in enumerate(evts):
				controls.setdefault(e_type, {})[e_id] = (action, mode)
		evthandler.add_event_handlers(dict.fromkeys(controls, self._joycb))

		# sun
		self.phys = Physics()
		p_data = conf.PLAYER_PLANET
		p_radius = p_data['radius']
		p_sun_dist = p_data['sun dist']
		pad = p_data['edge dist'] + p_sun_dist + p_radius
		s_w, s_h = conf.RES
		assert 2 * pad <= s_w and 2 * pad <= s_h
		sun = Sun(conf.SUN_DENSITY, conf.SUN_RADIUS, (uniform(pad, s_w - pad), uniform(pad, s_h - pad)))
		# players
		angle0 = uniform(0, 2 * pi)
		d_angle = 2 * pi / n_players
		self.players = [Player(i, self, p_data['density'], p_radius, sun, p_sun_dist, angle0 + i * d_angle) for i in xrange(n_players)]
		# extra planets
		planets = list(self.players)

		asteroids = []
		self.phys.gravity_sources = [sun] + planets
		self.entities = self.phys.gravity_sources + asteroids
		self.graphics.add(*(e.graphic for e in self.entities))

	def _joycb (self, evt):
		p = self.players[evt.joy]
		e_ident = evt.button if evt.type == pg.JOYBUTTONDOWN else evt.axis
		action, mode = self.controls[evt.type][e_ident]
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
		for p in self.players:
			p.update_path(sfc)
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
						# TODO: collide with missiles
						# TODO: collide with force fields
						collided_with = ast.collide_with_list(es)
						try:
							while True:
								ent = next(collided_with)
								if ent.hit_by_asteroid(ast):
									self.rm_ast(ast)
									break
						except StopIteration:
							pass

	def add_ast (self, ast):
		self.entities.append(ast)
		self.graphics.add(ast.graphic)

	def rm_ast (self, ast):
		self.entities.remove(ast)
		self.graphics.rm(ast.graphic)
