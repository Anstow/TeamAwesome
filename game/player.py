from math import cos, sin, atan2, pi
from util import Vect, blank_sfc, position_sfc
from conf import conf

import gm
import pygame as pg

from planet import Planet, Asteroid

class Dot (gm.Image):
	def __init__ (self, pos, sfc):
		gm.Image.__init__(self, pos, sfc)
		r = pg.Rect(self.rect)
		r.center = pos
		self.rect = r
		self.layer = conf.GRAPHICS_LAYERS['dot']

class Shield( CollisionEnt ):
    def __init__( self, player ):
		self.img = 'shield.png'.format(ident)
        self.owner = player
        self.angle = 0     # position
        self.size = pi/3   # size / 2 in rad
        self.image = ( "image0", "image1", "image2" )
        self.tech = 0
        self.thickness = 2
        self.damage = 0

        ### radius fudge factors
        self.f = 10
        self.s = 2
        self.world.scheduler.add_timeout( _self.repair, seconds = 1 )

    def _repair( self ):
        damage = max( damage - 1, 0 )

    def strength( self ):
        return max( 0, self.tech - self.damage )

    def get_radius( self ): 
        strength = self.strength(  )
        radius = 0

        if strength >= 0:
            radius = self.f + strength * self.s

        return radius
            
    def draw( self, angle )
        #strength = self.strength(  )
        #if strength >= 0:
        #   image = self.image[strength] 
        #   
        pass

    def 

    def collide_with_list ( self, collision_list ):
        r = self.radius()
        a0 = self.angle()
        a1 = clamp_ang( a0 + self.size )
        p = owner.pos

		for ent in collision_list:
			ep = ent.pos
            dif = [ ep[0] - p[0], 
			      ep[1] - p[1]]
            distance = ( dif[0]*dif[0] + dif[1]*dif[1] )**.5
            ent_ang = clamp_ang( acos( dif[0] / d_mag ) )

            if abs( d - r ) > self.thickness and ent is not self:
                if ent_ang > a0 and ent_ang < a0 + a1:
                    yield ent

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
		
        # Technology ( planet dies if < 0 )
        self.tech = 0
        self.world.scheduler.add_timeout( self._inc_tech, seconds = 15 )
        self.weapon = Shield( self )
        self.shield = Shield( self )

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

    def _inc_tech ( self ):
        tech += 1

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

	def pause (self, mode, evt):
		# horrible, but I like it somehow
		self.world.pause(player = self.player_ident)

	def move (self, phys, dt):
        #Actual movement
		Planet.move(self, phys, dt)
		self._since_last_launch += dt
		angle = self.aiming_angle[1]

        #A mockery of programming practice


	def update_path (self, dot_sfc):
		# update future path
		self.world.graphics.rm(*self._dots)
		self._dots = [Dot(p, dot_sfc) for p in self.world.phys.predict_future_positions(self._init_ast(), self.n_dots, conf.PLAYER_DOT_DISTANCE)]
		self.world.graphics.add(*self._dots)

    def hit_by_asteroid( self, ast ):
        self.tech -= 1
        if self.tech < 0:
            player.world.rm_player( self )
            if world
        return True
