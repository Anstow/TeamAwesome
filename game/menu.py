from world import World
import gm
from conf import conf
import pygame
import pygame.joystick as js
from ext import evthandler as eh
from util import blank_sfc, position_sfc

class Menu( World ):
	def __init__( self, scheduler, evthandler ):
		World.__init__( self, scheduler, evthandler )
		self.num_players = 1;
		self.num_joysticks = 0;

		#Create a background
		bg = gm.Colour(((0, 0), conf.RES), (0, 0, 0))
		bg.layer = 1
		self.graphics.add(bg)

		#Register event listeners
		evthandler.add_key_handlers(
				[( conf.KEYS_NEXT, self._load_joysticks, eh.MODE_ONDOWN )] )

		evthandler.add_event_handlers( { pygame.JOYBUTTONDOWN: self._handle_joystick } )

	def select( self ):
		###Load menu text images

		#Create blank surface with screen size
		blank = blank_sfc( conf.RES )

		#Create centred text image
		text_surface = conf.GAME.render_text( "menu",
			"Orbits\nPress Enter to reload controllers",
			( 0xFF, 0xFF, 0xFF ), just = 1, line_spacing = 30)[0]

		#Blit text to blank surface
		position_sfc( text_surface, blank )

		#Store image version of blitted surface
		self.text = gm.Image( ( 0, 0 ), blank )

		#Add image to graphics manager draw list
		self.graphics.add( self.text )

		self._load_joysticks()

	#### Event Handlers ####

	def _load_joysticks( self, *args ):
		#Clear current list of joysticks
		self.joysticks		  = []
		self.states			  = []
		self.active_joysticks = [False] * 4
		self.active_players   = [False] * 4

		#Reinitialize pygame.joystick to update joystick information
		js.quit()
		js.init()

		self.num_joysticks = js.get_count()

		#Create Joystick instance for each physical joystick
		for i in xrange( self.num_joysticks ):
			self.joysticks.append( js.Joystick( i ) )
			self.joysticks[i].init()

		#Draw state information
		for i in xrange( self.num_joysticks ):
			self.states.append( ControllerState( i, self.graphics ) )
			self.states[i].update(self.active_joysticks[i], self.active_players[i] )

	def _handle_joystick( self, evt ):
		#Store joystick id to use as index
		joystick = evt.joy

		#If A pressed, activate the joystick
		if evt.button == 0:
			self.active_joysticks[joystick] = True
		#If B pressed,  deactivate joystick and mark player as inactive
		elif evt.button == 1:
			self.active_joysticks[joystick] = False
			self.active_players  [joystick] = False
		#If Start pressed and joystick active, toggle player activity
		elif evt.button == 7 and self.active_joysticks[joystick]:
			self.active_players[joystick] = not self.active_players[joystick]

		#Draw state information
		for i in xrange( self.num_joysticks ):
			self.states[i].update(self.active_joysticks[i], self.active_players[i] )

		if self._start_game():
			print "Game started!"

	#Check start condition of the game
	def _start_game( self ):
		if self.active_players.count( True ) < 2:
			return False

		for i in xrange( self.num_joysticks ):
			if self.active_joysticks[i]:
				if not self.active_players[i]:
					return False

		return True

class ControllerState:
	def __init__( self, num, gfx ):
		self.num = num
		self.status_text = None
		self.ready_text = None
		self.pos = [ 0, 0 ]
		self.gfx = gfx
		if num == 1 or num == 3:
			self.pos[0] = conf.RES[0] - 100
		elif num == 2 or num == 3:
			self.pos[1] = conf.RES[1] - 20


	def update( self, active, playing ):
		if self.status_text is not None:
			print "Removing status text"
			self.gfx.rm( self.status_text )
		if self.ready_text is not None:
			self.gfx.rm( self.status_text )

		if active == True:
			if playing == True:
				self.status_text = gm.Image( self.pos,
					conf.GAME.render_text( "menu", "Player " + str( self.num ),
						( 0xFF, 0xFF, 0xFF ) )[0] )
				self.ready_text = gm.Image( self.pos,
					conf.GAME.render_text( "menu", "Press Start",
						( 0xFF, 0xFF, 0xFF ) )[0] )

				print "Controller ", self.num, "Active"
			else: #playing == True
				self.status_text = gm.Image( self.pos,
					conf.GAME.render_text( "menu", "Player " + str( self.num ),
						( 0x00, 0xFF, 0x00 ) )[0] )
				self.ready_text = gm.Image( self.pos,
					conf.GAME.render_text( "menu", "Ready!",
						( 0x00, 0xFF, 0x00 ) )[0] )
				print "Controller ", self.num, "Active and playing"

			self.gfx.add( self.ready_text )
			self.gfx.add( self.status_text )
		else: #active == False
			self.status_text = gm.Image( self.pos,
				conf.GAME.render_text( "menu", "Press A",
					( 0x99, 0x99, 0x99 ) )[0] )
			print "Controller ", self.num, "Inactive"
			self.gfx.add( self.status_text )
