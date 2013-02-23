from conf import conf
from world import World
import gm
from planet import Planet
from physics import Physics


class Level (World):
    def __init__ (self, scheduler, evthandler):
        World.__init__(self, scheduler, evthandler)
        self.phys = Physics()
        add_graphic = self.graphics.add
        bg = gm.Colour(((0, 0), conf.RES), (0, 0, 0))
        add_graphic(bg)
        bg.layer = conf.GRAPHICS_LAYERS['bg']
        add_graphic(Planet(self, 1, (500, 300), 100, 0).graphic)

    #def update (self):
        #self.phys.update()
