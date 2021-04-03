import os
import time
import pygame
import neat
import random
pygame.font.init()
WIN_HEIGHT = 800
WIN_WIDTH = 500
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
BIRDIMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", 'bird1.png')).convert_alpha()), pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", 'bird2.png')).convert_alpha()), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", 'bird2.png')).convert_alpha())]
PIPEIMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", 'pipe.png')).convert_alpha())
BASEIMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", 'base.png')).convert_alpha())
BGIMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", 'bg.png')).convert_alpha())


STAT_FONT = pygame.font.SysFont('comicsans', 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = True

gen = 0


class Bird:
    IMGS = BIRDIMGS
    MAXROT = 25
    ROTVEL = 20
    ANIM_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        # s = ut + 0.5at^2 here -d means going up and +d means going down
        d = self.vel*(self.tick_count) + 0.5 * \
            (3)*(self.tick_count)**2
        # fine tuning movement
        if d >= 16:
            d = 16  # terminal velocity
        if d < 0:
            d -= 2
        self.y = self.y + d
        if d < 0 or self.y < self.height + 50:  # dont tilt bird until it falling below init pos
            if self.tilt < self.MAXROT:
                self.tilt = self.MAXROT
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTVEL  # while diving do nosedive

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIM_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIM_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIM_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIM_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIM_TIME * 5:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIM_TIME*2
        # better to define func
        # rotated_img = pygame.transform.rotate(
        #     self.img, self.tilt)  # rotate img around topleft corner
        # new_react = rotated_img.get_rect(center=self.img.get_rect(
        #     topleft=(self.x, self.y)).center)  # to transform rotatn arounf center
        # win.blit(rotated_img, new_react.topleft)  # blit == draw
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PT = pygame.transform.flip(PIPEIMG, False, True)
        self.PB = PIPEIMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PT.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PT, (self.x, self.top))
        win.blit(self.PB, (self.x, self.bottom))

    def collide(self, bird, win):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PT)
        bottom_mask = pygame.mask.from_surface(self.PB)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        return False


class Base:
    VEL = 5
    WIDTH = BASEIMG.get_width()
    IMG = BASEIMG

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


# testing
def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=topleft).center)

    surf.blit(rotated_image, new_rect.topleft)


def draw_win(win, birds, pipes, base, score, gen, pipe_ind):
    win.blit(BGIMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (250, 250, 250))
    win.blit(text, (WIN_WIDTH-10 - text.get_width(), 10))
    base.draw(win)
    for bird in birds:
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255, 0, 0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height(
                )/2), (pipes[pipe_ind].x + pipes[pipe_ind].PT.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255, 0, 0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height(
                )/2), (pipes[pipe_ind].x + pipes[pipe_ind].PB.get_width()/2, pipes[pipe_ind].bottom), 5)
            except Exception as e:
                # print(e)
                pass
        bird.draw(win)    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render(
        "Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_gene(genome, config):
    nets = []
    ge = []
    birds = []
    global WIN, gen
    win = WIN
    gen += 1
    for __, g in genome:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))

        ge.append(g)
    #win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    base = Base(730)
    pipes = [Pipe(450)]
    run = True
    score = 0
    clock = pygame.time.Clock()

    while(run) and len(birds) > 0:
        clock.tick(30)
        rem = []
        add_pipe = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        ppind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PT.get_width():
                ppind = 1

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = nets[x].activate(
                (bird.y, abs(bird.y - pipes[ppind].height), abs(bird.y - pipes[ppind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        for pipe in pipes:
            pipe.move()
            for x, bird in enumerate(birds):
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            if pipe.x + pipe.PT.get_width() < 0:
                rem.append(pipe)

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(550))
        for r in rem:
            pipes.remove(r)
        base.move()
        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= 730 or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        # bird.move()
        draw_win(WIN, birds, pipes, base, score, gen, ppind)


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_gene, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
