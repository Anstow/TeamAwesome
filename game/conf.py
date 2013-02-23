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
	USE_FONTS = False

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
	SOUND_DIR = DATA_DIR + 'sound' + sep
	MUSIC_DIR = DATA_DIR + 'music' + sep
	FONT_DIR = DATA_DIR + 'font' + sep

	# display
	WINDOW_ICON = None #IMG_DIR + 'icon.png'
	WINDOW_TITLE = ''
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

	# audio
	MUSIC_AUTOPLAY = False # just pauses music
	MUSIC_VOLUME = dd(.5) # per-backend
	SOUND_VOLUME = .5
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
	REQUIRED_FONTS = dd({})

	# physics
	DEFAULT_TIME_OFFSET = 0.015
	GRAVITY_CONSTANT = 1

	# graphics
	GRAPHICS_LAYERS = {
		'bg': 0,
		'sun': -1,
		'planet': -2,
		'asteroid': -3
	}

	# level generation
	SUN_DENSITY = 100
	SUN_RADIUS = 30
	PLAYER_PLANET_DATA = {
		'density': 10,
		'radius': 8,
		'sun dist': 200,
		'edge dist': 110
	}


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
