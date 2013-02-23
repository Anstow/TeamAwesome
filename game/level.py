from math import cos, sin, atan2, pi
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
		self.launch_speed = conf.ASTEROID_LAUNCH_SPEED
		self._since_last_launch = conf.ASTEROID_LAUNCH_GAP
		self.aiming = [[0, 0], [0, 0]] # (defensive, offensive) (x, y)
		self.aiming_angle = [0, 0]
		self._fire_last = [0, 0] # (defensive, offensive) - since fire are axes
		Planet.__init__(self, *args)

	def aim (self, mode, evt):
		action = mode >= 2
		v = self.aiming[action]
		v[mode % 2] = evt.value
		x, y = v
		self.aiming_angle[action] = atan2(y, x)

	def fire (self, mode, evt):
		last = self._fire_last[mode]
		now = evt.value
		if last < conf.TRIGGER_THRESHOLD and now >= conf.TRIGGER_THRESHOLD:
			if mode == 1 and self._since_last_launch >= conf.ASTEROID_LAUNCH_GAP:
				# fire asteroid
				angle = self.aiming_angle[mode]
				a = Asteroid(self.pos, (self.launch_speed * cos(angle), self.launch_speed * sin(angle)))
				self.world.add_ast(a)
				self._since_last_launch -= conf.ASTEROID_LAUNCH_GAP
		self._fire_last[mode] = now

	def move (self, phys, dt):
		Planet.move(self, phys, dt)
		self._since_last_launch += dt


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

	def collision_detection(self):
		es = self.entities
		dist = conf.ASTEROID_DESTROY_DIST * 2
		in_bdy = pg.Rect((0, 0), conf.RES).inflate(dist, dist).collidepoint
		for ast in es:
			if isinstance(ast, Asteroid):
				if not in_bdy(ast.pos):
					self.rm_ast(ast)
				else:
					# Firstly collide with everthing
					# TODO: collide with missiles
					# TODO: collide with force fields
					collided_with = ast.collide_with_list(es)
					try:
						ent = next(collided_with)
					except StopIteration:
						pass
					else:
						# TODO: collision resolution, this should be done by overriding hit_by_asteroid
						ent.hit_by_asteroid(ast)

	def add_ast (self, ast):
		self.entities.append(ast)
		self.graphics.add(ast.graphic)

	def rm_ast (self, ast):
		self.entities.remove(ast)
		self.graphics.rm(ast.graphic)
