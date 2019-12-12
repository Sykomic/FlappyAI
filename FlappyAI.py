import pygame as pg
import neat
import time
import os
import random

WIN_WIDTH = 600
WIN_HEIGHT = 800

BIRD_IMGS = [
        pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird1.png'))),
        pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird2.png'))),
        pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird3.png')))
        ]
