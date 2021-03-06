# coding=utf-8

from platform import system
import os
from os.path import sep, expanduser, join as join_path
from collections import defaultdict
from glob import glob

import pygame as pg

import settings
from util import dd


class Conf (object):

	IDENT = 'game'
	USE_SAVEDATA = False
	USE_FONTS = True

	# the Game instance; should only really be used to load media with caching
	GAME = None

	# save data
	SAVE = ()
	# need to take care to get unicode path
	if system() == 'Windows':
		try:
			import ctypes
			n = ctypes.windll.kernel32.GetEnvironmentVariableW(u'APPDATA',
																None, 0)
			if n == 0:
				raise ValueError()
		except Exception:
			# fallback (doesn't get unicode string)
			CONF_DIR = os.environ[u'APPDATA']
		else:
			buf = ctypes.create_unicode_buffer(u'\0' * n)
			ctypes.windll.kernel32.GetEnvironmentVariableW(u'APPDATA', buf, n)
			CONF_DIR = buf.value
		CONF_DIR = join_path(CONF_DIR, IDENT)
	else:
		CONF_DIR = join_path(os.path.expanduser(u'~'), '.config', IDENT)
	CONF = join_path(CONF_DIR, 'conf')

	# data paths
	DATA_DIR = ''
	IMG_DIR = DATA_DIR + 'img' + sep
	SOUND_DIR = DATA_DIR + 'snd' + sep
	MUSIC_DIR = DATA_DIR + 'music' + sep
	FONT_DIR = DATA_DIR + 'font' + sep

	# display
	WINDOW_ICON = IMG_DIR + 'icon.png'
	WINDOW_TITLE = 'Orbits'
	MOUSE_VISIBLE = dd(False) # per-backend
	FLAGS = 0
	FULLSCREEN = False
	RESIZABLE = False # also determines whether fullscreen togglable
	RES_W = (960, 720)
	RES_F = pg.display.list_modes()[0]
	RES = RES_W
	MIN_RES_W = (320, 180)
	ASPECT_RATIO = None

	# timing
	FPS = dd(60) # per-backend

	# debug
	PROFILE_STATS_FILE = '.profile_stats'
	DEFAULT_PROFILE_TIME = 5

	# input
	KEYS_NEXT = (pg.K_RETURN, pg.K_SPACE, pg.K_KP_ENTER)
	KEYS_BACK = (pg.K_ESCAPE, pg.K_BACKSPACE)
	KEYS_MINIMISE = (pg.K_F10,)
	KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
					(pg.K_KP_ENTER, pg.KMOD_ALT, True))
	KEYS_LEFT = (pg.K_LEFT, pg.K_a, pg.K_q)
	KEYS_RIGHT = (pg.K_RIGHT, pg.K_d, pg.K_e)
	KEYS_UP = (pg.K_UP, pg.K_w, pg.K_z, pg.K_COMMA)
	KEYS_DOWN = (pg.K_DOWN, pg.K_s, pg.K_o)
	KEYS_DIRN = (KEYS_LEFT, KEYS_UP, KEYS_RIGHT, KEYS_DOWN)
	KEYS_QUIT = (pg.K_q, pg.K_x)
	# controllers
	CONTROLS = {
		'aim': ( # defensive, offensive
            ((pg.JOYAXISMOTION, 0), (pg.JOYAXISMOTION, 1), (pg.JOYAXISMOTION, 4), (pg.JOYAXISMOTION, 3))
            if system() == 'Windows' else
            ((pg.JOYAXISMOTION, 0), (pg.JOYAXISMOTION, 1), (pg.JOYAXISMOTION, 3), (pg.JOYAXISMOTION, 4))
        ),
		'fire': ((pg.JOYAXISMOTION, 2), (pg.JOYAXISMOTION, 2 if system() == 'Windows' else 5)),
		'pause': ((pg.JOYBUTTONDOWN, 7),),
		#'scroll': ((pg.JOYBUTTONDOWN, 4), (pg.JOYBUTTONDOWN, 5)),
		#'select': ((pg.JOYBUTTONDOWN, 0),)
	}
	TRIGGER_THRESHOLD = .5 if system() == 'Windows' else 0
	AIM_THRESHOLD = .4

	# audio
	MUSIC_AUTOPLAY = True # just pauses music
	MUSIC_VOLUME = dd(.8) # per-backend
	SOUND_VOLUME = .8
	EVENT_ENDMUSIC = pg.USEREVENT
	SOUND_VOLUMES = dd(1)
	# generate SOUNDS = {ID: num_sounds}
	SOUNDS = {}
	ss = glob(join_path(SOUND_DIR, '*.ogg'))
	base = len(join_path(SOUND_DIR, ''))
	for fn in ss:
		fn = fn[base:-4]
		for i in xrange(len(fn)):
			if fn[i:].isdigit():
				# found a valid file
				ident = fn[:i]
				if ident:
					n = SOUNDS.get(ident, 0)
					SOUNDS[ident] = n + 1

	# text rendering
	# per-backend, each a {key: value} dict to update Game.fonts with
	REQUIRED_FONTS = dd({ "menu": ( "WireOne.ttf", 40 )})

	# physics
	DEFAULT_TIME_OFFSET = 0.015
	GRAVITY_CONSTANT = 1
	ASTEROID_DESTROY_DIST = 300 # outside screen borders
	FORCEFIELD_ANGLE = 70 # degrees

	# graphics
	GRAPHICS_LAYERS = {
		'bg': 0,
		'sun': -1,
		'planet': -2,
		'asteroid': -3,
		'dot': -4
	}
	IMG_OFFSETS = dd(0, sun = 65, player0 = 8)
	AIM_ANGLE_CHANGE_UPDATE = .08
	PATH_UPDATE_TIME = .05
	MENU_LINE_SPACING = 30

	# level generation
	# sun
	SUN_DENSITY = 400
	SUN_RADIUS = 25
	# npp (non player planet)
	INNER_PLANET = {
		'density': 800,
		'min radius': 5,
		'max radius': 7,
		'min sun dist': 185,
		'max sun dist': 270,
		'number': 1
	}
	OUTER_PLANET = {
		'density': 900,
		'min radius': 8,
		'max radius': 20,
		'min sun dist': 330,
		'max sun dist': 450,
		'number': 3
	}
	# player
	PLAYER_PLANET = {
		'density': 300,
		'radius': 12,
		'sun dist': 250,
		'edge dist': 90
	}
	ASTEROID_LAUNCH_SPEED = 300
	ASTEROID_LAUNCH_DIST = 25 # from player
	ASTEROID_LAUNCH_GAP = 1 # seconds
	DOT_RADIUS = 2

	# gameplay
	PLAYER_N_DOTS = 12
	PLAYER_DOT_DISTANCE = 5 # multiple of DEFAULT_TIME_OFFSET
	# asteroid
	ASTEROID = {
		'density': 0.8,
		'min radius': 1,
		'max radius': 7
	}

	# colours
	P_COLOURS = [( 0xAC, 0x19, 0x27 ), 
				 ( 0x0A, 0xAF, 0xE7 ), 
				 ( 0xe9, 0xa7, 0x07 ), 
				 ( 0xE6, 0xff, 0xf9 ) ]


def translate_dd (d):
    if isinstance(d, defaultdict):
        return defaultdict(d.default_factory, d)
    else:
        # should be (default, dict)
        return dd(*d)
conf = dict((k, v) for k, v in Conf.__dict__.iteritems()
            if k.isupper() and not k.startswith('__'))
types = {
    defaultdict: translate_dd
}
if Conf.USE_SAVEDATA:
    conf = settings.SettingsManager(conf, Conf.CONF, Conf.SAVE, types)
else:
    conf = settings.DummySettingsManager(conf, types)
