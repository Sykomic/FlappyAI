import sys
import pygame as pg
import neat
import time
import os
import random
import pickle
pg.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800
GEN = 0
GOOD = False

BIRD_IMGS = [
        pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird1.png'))),
        pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird2.png'))),
        pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird3.png')))
        ]
PIPE_IMG = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'pipe.png')))
BASE_IMG = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'base.png')))
BG_IMG = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bg.png')))

STAT_FONT = pg.font.SysFont("comicsans", 50)

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
        self.vel = -5 # on pygame, going up is decreasing. original : 10.5
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
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Checking if bird and pipe collide, otherwise it returns None
        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        if t_point or b_point:
            return True
        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window2(win, birds, pipes, base, score, gen, alive):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    text = STAT_FONT.render("Alive: " + str(alive), 1, (255, 255, 255))
    win.blit(text, (10, 50))

    base.draw(win)
    for bird in birds:
        bird.draw(win)

    pg.display.update()

def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)
    bird.draw(win)
    pg.display.update()

def eval_genome(genome, config, load = False, trained = False):
    global GEN, GOOD
    GEN += 1

    nets = []
    ge = []
    birds = []

    for _, g in genome: # (genome_id, genome_obj)
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pg.time.Clock()
    score = 0

    run = True
    while run:
        if trained:
            clock.tick(30)
        else:
            clock.tick(100)
        if score >= 50 and load == False:
            GOOD = True
            run = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                pg.quit()
                quit()
        pipe_ind = 0
        if len(birds) > 0:
            # if birds pass the first pipe, then pass the second pipe's info to nn.
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else: # no birds left then game over.
            run = False
            break

        for i, bird in enumerate(birds):
            bird.move()
            ge[i].fitness += 0.1 # give reward when a bird is moving forward.
            distTopPipe = bird.y - pipes[pipe_ind].height
            distBottomePipe = bird.y - pipes[pipe_ind].bottom

            outputs = nets[i].activate((bird.y, abs(distTopPipe), abs(distBottomePipe)))

            if outputs[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []  # removed pipes
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird, win):
                    ge[i].fitness -= 1  # decrease fitness score by 1
                    birds.pop(i) # remove the bird object
                    nets.pop(i)
                    ge.pop(i)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            pipe.move()
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for i, bird in enumerate(birds):
            # may have issue because we are removing an item while looping through
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                # a bird might go below or above the screen and never dies.
                birds.pop(i) # remove the bird object
                nets.pop(i)
                ge.pop(i)

        base.move()
        draw_window2(win, birds, pipes, base, score, GEN, len(birds))

def main():
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)]
    win = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pg.time.Clock()
    score = 0

    run = True
    over = False
    while run:
        clock.tick(30)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                pg.quit()
                quit()
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE]:
            #ticker = 30
            bird.jump()
            bird.move()
        bird.move()

        add_pipe = False
        rem = []  # removed pipes

        for pipe in pipes:
            if pipe.collide(bird, win):
                over = True
                break
            if bird.y + bird.img.get_height() >= 730:
                over = True
                break
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            pipe.move()
        if over:
            gameover(win, score)
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        main()
        else:
            if add_pipe:
                score += 1
                pipes.append(Pipe(600))

            for r in rem:
                pipes.remove(r)

            base.move()
            draw_window(win, bird, pipes, base, score)
    #pg.quit()
    #quit()

def gameover(win, score):
    win.blit(BG_IMG, (0, 0))
    text = STAT_FONT.render("Game Over!", 1, (255, 255, 255))
    text_width = text.get_width()
    text_height = text.get_height()
    center = (WIN_WIDTH / 2 - text_width / 2, WIN_HEIGHT / 2 - text_height / 2 - 50)
    win.blit(text, center)
    text = STAT_FONT.render("You scored " + str(score) + " Points", 1, (255, 255, 255))
    text_width = text.get_width()
    text_height = text.get_height()
    center = (WIN_WIDTH / 2 - text_width / 2, WIN_HEIGHT / 2 - text_height / 2)
    win.blit(text, center)
    text = STAT_FONT.render("Press space bar to play again", 1, (255, 255, 255))
    text_width = text.get_width()
    text_height = text.get_height()
    center = (WIN_WIDTH / 2 - text_width / 2, WIN_HEIGHT / 2 - text_height / 2 + 50)
    win.blit(text, center)

    pg.display.update()

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
    neat.DefaultSpeciesSet, neat.DefaultStagnation,
    config_path)

    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    winner = pop.run(eval_genome, 50) # 50 population of main method
    if GOOD == True:
        with open('model_pickle', 'wb') as f:
            pickle.dump(winner, f)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'NEAT_CONFIG.txt')
    if len(sys.argv) == 2:
        if sys.argv[1] == '-m':
            main()
        elif sys.argv[1] == '-ai':
            run(config_path)
        elif sys.argv[1] == '-p': # Load a trained flappy bird.
            config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
            neat.DefaultSpeciesSet, neat.DefaultStagnation,
            config_path)
            with open('model_pickle', 'rb') as f:
                genome = pickle.load(f)
            genomes = [(1, genome)]
            eval_genome(genomes, config, True, True)
    else:
        main()
