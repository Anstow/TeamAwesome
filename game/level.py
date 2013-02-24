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






# Level



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

    def num_players(  ):
        return _self.players.count( not None )

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

	def pause (self):
		pass
