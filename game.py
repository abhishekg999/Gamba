import random
import math
import os
import sys
import pygame as pg

from keyhandler import KeyHandler

# constants
WINSIZE = [640, 480]
WINCENTER = [x/2 for x in WINSIZE]


white = 255, 240, 200
black = 20, 20, 40


class PgMusic():
    def __init__(self, source, playonload=False, start=None):
        self.music = pg.mixer.music
        self.started = False
        self.paused = None

        self.music.load(source)
        if playonload:
            self.music.play()
            if start:
                self.music.set_pos(start)
            self.started = True
            self.paused = False


    def getMusic(self):
        return self.music

    def pause(self):
        self.music.pause()
        self.paused = True

    def unpause(self):
        self.music.unpause()
        self.paused = False

    def toggle(self):
        if not self.started:
            self.music.play()
            self.started = True
            self.paused = False

        else:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        

class UIInteractable():
    def __init__(self, app, x, y, dx=0, dy=0, img=None, color=pg.Color(0, 255, 0), dynamic=False):
        self.app = app

        self.dynamic = dynamic
        self.x = x 
        self.y = y 

        self.color = color
        self.dx, self.dy = dx, dy 

        if img is not None:
            self.image = pg.image.load(img)
            self.image.convert_alpha()
            self.surface = self.image
            self.dx, self.dy = self.surface.get_size()
        else:
            if self.dynamic:
                self.resize()

            else:
                self.surface = pg.Surface((self.dx, self.dy))
                self.surface.fill(self.color)
        
        self.dim = [range(self.x, self.x + self.dx), range(self.y, self.y + self.dy)]


    def isClicked(self, mouse):
        self.mouse_coord = mouse.get_pos()
        #print(self.mouse_coord)
        #print(self.dim)
        if self.mouse_coord[0] in self.dim[0] and self.mouse_coord[1] in self.dim[1]:
            print(True)
            self.clickEvent()
            return True

        return False

    def clickEvent(self):
        #print("asdf")
        pass

    def blit(self):
        self.app.screen.blit(self.surface, (self.x, self.y))

    def resize(self):
        if self.dynamic:
            self.windim = pg.display.get_window_size()
            self.dx = int(self.windim[0] * self.dx/100.0)
            self.dy = int(self.windim[1] * self.dy/100.0)
            self.dim = [range(self.x, self.x + self.dx), range(self.y, self.y + self.dy)]

            self.surface = pg.Surface((self.dx, self.dy))
            self.surface.fill(self.color)

    def event(self):
        pass

class Button(UIInteractable):
    def __init__(self, app, x, y, dx=0, dy=0, img=None, color=pg.Color(0, 255, 0), dynamic=False):
        super().__init__(app, x, y, dx, dy, img=img, color=color, dynamic=dynamic)

    def clickEvent(self):
        print("click")
        self.app.m.toggle()


class App():
    def __init__(self):
        random.seed()
        self.clock = pg.time.Clock()
        #self.screen = pg.display.set_mode(WINSIZE, flags=pg.RESIZABLE)
        self.screen = pg.display.set_mode(WINSIZE)
        self.mouse = None

        self.done = 0
        self.things = []

    def run(self):
        random.seed()
        self.clock = pg.time.Clock()

        pg.init()
        #screen = pg.display.set_mode(WINSIZE, flags=pg.RESIZABLE)
        pg.display.set_caption("OSU Mapper")

        self.mouse = pg.mouse
        self.mouse.set_visible(False)


        self.cursor = pg.image.load("cursor.png")
        self.cursor.convert_alpha()

        #self.hitcircle = pg.image.load("hitcircle.png")
        #self.hitcircle.convert_alpha()

        #self.m = PgMusic("audio.mp3", True)

        self.button = Button(self, 0, 0, 50, 50)
        self.things += [self.button]
       
        ###### PUT IN OSUSong ######
        self.m = PgMusic("quaver.mp3", True, start=0)

        self.currentTime = -1
        #self.song = OSUSong(self, "map.klk", 272.727272727273, 6, 1021.85303388495)

        self.ofb = OSUFileBuilder("quaver.mp3", "Quaver - Abhi", 329.67032967033, 4, 1198)






       #############################

        while not self.done:
            self.currentTime = self.m.getMusic().get_pos()

            for e in pg.event.get():
                if e.type == pg.QUIT or (e.type == pg.KEYUP and e.key == pg.K_ESCAPE):
                    self.done = 1
                    break

                if e.type == pg.KEYUP and e.key == pg.K_SPACE:
                    print("sdkjahfksdf")
                    self.m.toggle()

                if e.type == pg.KEYDOWN:
                    for key in CLICKKEYS:
                        if e.key == key.key and key.isClicked:
                            print("-------------\n-------------\nclick\n-------------\n-------------\n")
                            for x in self.things:
                                if x.isClicked(self.mouse):
                                    break

                            self.ofb.addHitObject(self.mouse.get_pos()[0], self.mouse.get_pos()[1], self.currentTime)

                if e.type == pg.KEYUP:
                    for key in CLICKKEYS:
                        if e.key == key.key:
                            key.onKeyUp()
                           
                if e.type == pg.MOUSEBUTTONUP:
                    for x in self.things:
                        if x.isClicked(self.mouse):
                            break


                if e.type == pg.VIDEORESIZE:
                    for x in self.things:
                        x.resize()

            

            for x in self.things:
                x.event()

            #self.song.step(self.currentTime)

            pg.display.set_caption("OSU Mapper" + " | " + "{} | {}".format(self.currentTime, self.clock.get_fps()))

            self.screen.fill(black)      
            for x in self.things:
                x.blit()
            self.screen.blit(self.cursor, (tuple([self.mouse.get_pos()[x] - self.cursor.get_size()[x]/2 for x in range(2)])))

            pg.display.update()
            self.clock.tick(200)

        self.ofb.writeFile("song.osu")





if __name__ == "__main__":
    thing = App()
    thing.run()
