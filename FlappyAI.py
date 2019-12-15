import pygame as pg
import neat
import time
import os
import random

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [
        pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird1.png'))),
        pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird2.png'))),
        pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird3.png')))
        ]
PIPE_IMG = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'pipe.png')))
BASE_IMG = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'base.png')))
BG_IMG = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bg.png')))

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5 # on pygame, going up is decreasing.
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1  # How many time we are moving
        # Moving up or down
        d = self.vel * self.tick_count + 1.5 * self.tick_count**2
        if d >= 16:
            d = 16
        if d < 0:
            d -= 2
        self.y += d
        # when a bird is going up, tilt it to make it look going up.
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else: # When a bird is going down, tilt it to make it look going down.
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # Based on img_count, flip the bird's wing.
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2
        # Rotate images around the center.
        rotated_image = pg.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(
                                            topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

# Mask -> check where all the pixels in images. it is used for collision check
    def get_mask(self):
        return pg.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pg.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False #If a bird passed a pipe, it's for collision
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird, win):
        bird_mask = bird.get_mask()
        top_mask = pg.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pg.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x)

        # Pixel Perfect Collision 11:30



def draw_window(win, bird):
    win.blit(BG_IMG, (0, 0))
    bird.draw(win)
    pg.display.update()


def main():
    bird = Bird(200, 200)
    run = True
    win = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pg.time.Clock()

    while run:
        clock.tick(30)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
        #bird.move()
        draw_window(win, bird)
    pg.quit()
    quit()

main()
