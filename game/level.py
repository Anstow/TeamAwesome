from conf import conf
from world import World
import gm
from planet import Planet, Asteroid
from physics import Physics


class Level (World):
    def __init__ (self, scheduler, evthandler):
        World.__init__(self, scheduler, evthandler)
        self.phys = Physics()
        add_graphics = self.graphics.add
        bg = gm.Colour(((0, 0), conf.RES), (0, 0, 0))
        add_graphics(bg)
        bg.layer = conf.GRAPHICS_LAYERS['bg']
        sun = Planet(self, 10, 50, (500, 300))
        self.phys.gravity_sources.append(sun)
        planets = [Planet(self, 150, 20, sun, 200, 0)]
        self.phys.gravity_sources += planets
        self.asteroids = [Asteroid((300, 300), (0, -70))]
        add_graphics(sun.graphic, *(p.graphic for p in planets + self.asteroids))
        self.t = 0
        self.scheduler.interp(lambda t: t, self.update_t)

    def update_t (self, t):
		phys = self.phys
		dt = t - self.t
		self.t = t
		for s in phys.gravity_sources:
			s.move(dt)
		for a in self.asteroids:
			a.move(phys, dt)
