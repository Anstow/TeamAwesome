from platform import system
is_win = system() == 'Windows'
from math import cos, sin, atan2, pi
from util import Vect, blank_sfc, position_sfc
from conf import conf

import gm
import pygame as pg

from planet import Planet, Asteroid

class Dot (gm.Graphic):
	def __init__ (self, sfc, pos):
		gm.Graphic.__init__(self, sfc, pos)
		r = pg.Rect(self.rect)
		r.center = pos
		self.rect = r
		self.layer = conf.GRAPHICS_LAYERS['dot']


class Player (Planet):
	def __init__ (self, ident, *args):
		self.player_ident = ident
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

		self.score = 0

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
		if is_win:
			now *= -1
		if last < conf.TRIGGER_THRESHOLD and now >= conf.TRIGGER_THRESHOLD:
			if mode == 1 and self._since_last_launch >= conf.ASTEROID_LAUNCH_GAP:
				# fire asteroid
				pos, vel = self._init_ast()
				self.world.add_ast(Asteroid(self.world, pos, vel))
				self._since_last_launch = 0
		self._fire_last[mode] = now

	def pause (self, mode, evt):
		# horrible, but I like it somehow
		self.world.pause(player = self.player_ident)

	def move (self, phys, dt):
		Planet.move(self, phys, dt)
		self._since_last_launch += dt
		angle = self.aiming_angle[1]

	def update_path (self, dot_sfc):
		# update future path
		self.world.graphics.rm(*self._dots)
		self._dots = [Dot(dot_sfc, p) for p in self.world.phys.predict_future_positions(self._init_ast(), self.n_dots, conf.PLAYER_DOT_DISTANCE)]
		self.world.graphics.add(*self._dots)

	def increment_score(self):
		self.score += 1

	def hit_by_asteroid(self, asteroid):
		rtn = Planet.hit_by_asteroid(self, asteroid)
		self.score -= 1
		#asteroid.player.increment_score()
		return rtn
