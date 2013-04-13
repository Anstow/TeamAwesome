import gm

class PlayerHud:
	def __init__(self, player):
		self.player = player
		self.player_ident = player.player_ident
		self.player_text = "Player " + str(self.player_ident) + ": "
		self.player_score = str(player.score)
		self.pos = [ 20, 20 ]
		self.gfx = gfx
		if self.player_ident % 2 = 0:
			self.pos[0] = conf.RES[0] - 128
		if self.player_ident + 1 % 2 = 0:
			self.pos[1] = conf.RES[1] - 100
		

	def refresh (self):
		self.player_score = str(player.score)
		if self.player_text is not None:
			self.gfx.rm( self.status_text )
		if self.player_score is not None:
			self.gfx.rm( self.ready_text )
 

	def update( self, active, playing ):
		self.clear()

		if active == True:
			self.status_text = gm.Graphic(
				conf.GAME.render_text( "menu", "Player " + str( self.num + 1 ),
					conf.P_COLOURS[self.num] )[0], self.pos )
			if playing == False:
				self.ready_text = gm.Graphic(
					conf.GAME.render_text( "menu", "Press Start",
						( 0xFF, 0xFF, 0xFF ) )[0], self.readypos )

			else: #playing == True
				self.ready_text = gm.Graphic(
					conf.GAME.render_text( "menu", "Ready!",
						( 0x00, 0xFF, 0x00 ) )[0], self.readypos )

			self.gfx.add( self.ready_text )
			self.gfx.add( self.status_text )
		else: #active == False
			self.status_text = gm.Graphic(
				conf.GAME.render_text( "menu", "Press A",
					( 0x99, 0x99, 0x99 ) )[0], self.pos )
			self.gfx.add( self.status_text )
