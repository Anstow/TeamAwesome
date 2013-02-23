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
        self.planets = [Planet(self, 1, (500, 300), 100, 0)]
        self.phys.gravity_sources += self.planets
        add_graphics(*(p.graphic for p in self.planets))
        self.asteroids = [Asteroid((300, 200), (0, 0))]
        add_graphics(*(a.graphic for a in self.asteroids))
        self.scheduler.interp(lambda t: t, self.update_t)

    def update_t (self, t):
        phys = self.phys
        for a in self.asteroids:
            a.move(phys, t)
