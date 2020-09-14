import os
import sys
import pygame
import random
import neat
import datetime
from pygame import *

pygame.init()

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 400
GROUND_Y = WINDOW_HEIGHT - 50
SRC_FOLDER = "imgs"

DINO_RUN_IMGS = []
for i in range(2):
    DINO_RUN_IMGS.append((pygame.image.load(os.path.join(SRC_FOLDER, f"dinorun{i}.png"))))
DINO_DUCK_IMGS = []
for i in range(2):
    DINO_DUCK_IMGS.append(pygame.image.load(os.path.join(SRC_FOLDER, f"dinoduck{i}.png")))
DINO_JUMP = pygame.image.load(os.path.join(SRC_FOLDER, "dinojump.png"))

BIRD_IMGS = []
for i in range(2):
    BIRD_IMGS.append(pygame.image.load(os.path.join(SRC_FOLDER, f"berd{i}.png")))

CACTUS_IMGS = []
for i in range(3):
    CACTUS_IMGS.append(pygame.image.load(os.path.join(SRC_FOLDER, f"cactus{i}.png")))

GROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(SRC_FOLDER, "ground.png")))
BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join(SRC_FOLDER, "bg.png")), (WINDOW_WIDTH, WINDOW_HEIGHT))

# Font info
STAT_FONT = pygame.font.SysFont("comicsans", 50)
SCORE_FONT_COLOR = (255, 0, 100)
GENERATION_FONT_COLOR = (255, 0, 0)
DINO_COUNT_FONT_COLOR = (0, 255, 0)

GEN_NUM = 0
MAX_SCORE = 0
MAX_VEL = 0

class Dino:
    RUN_IMGS = DINO_RUN_IMGS
    DUCK_IMGS = DINO_DUCK_IMGS
    JUMP_IMG = DINO_JUMP
    ANIMATION_TIME = 10
    GRAVITY = 13

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.RUN_IMGS[0]
        self.is_jumping = False
        self.is_ducking = False
        self.is_falling = False
        self.duck_cnt = 0

    def jump(self):
        if not self.is_jumping and not self.is_falling:
            self.tick_count = 0
            self.height = self.y
            self.is_jumping = True

    def duck(self):
        self.is_ducking = True
        self.duck_cnt = 0

    def move(self):
        self.tick_count += 1

        if self.y < GROUND_Y - self.img.get_height() + 15:
            self.y += self.GRAVITY


    def checkbounds(self):
        if self.y < 40:
            self.is_jumping = False
            self.img_count = 0
            self.is_falling = True
        elif self.y >= GROUND_Y - self.img.get_height() + 15:
            self.is_falling = False

    def draw(self, window):
        self.img_count += 1
        self.duck_cnt += 1

        self.checkbounds()

        if self.duck_cnt % 2 == 0:
            self.is_ducking = False

        if self.is_jumping:
            self.img = self.JUMP_IMG
            self.y -= self.GRAVITY * 2

        elif self.is_falling:
            self.img = self.JUMP_IMG

        elif self.is_ducking:
            self.y = GROUND_Y - self.DUCK_IMGS[0].get_height() + 15
            if self.img_count <= self.ANIMATION_TIME:
                self.img = self.DUCK_IMGS[0]
            elif self.img_count <= self.ANIMATION_TIME * 2:
                self.img = self.DUCK_IMGS[1]
            elif self.img_count == self.ANIMATION_TIME * 2 + 1:
                self.img = self.DUCK_IMGS[0]
                self.img_count = 0

        else:
            self.y = GROUND_Y - self.RUN_IMGS[0].get_height() + 15
            if self.img_count <= self.ANIMATION_TIME:
                self.img = self.RUN_IMGS[0]
            elif self.img_count <= self.ANIMATION_TIME * 2:
                self.img = self.RUN_IMGS[1]
            elif self.img_count == self.ANIMATION_TIME * 2 + 1:
                self.img = self.RUN_IMGS[0]
                self.img_count = 0

        window.blit(self.img, (self.x, self.y))

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Base:
    VEL = 10
    WIDTH = GROUND_IMG.get_width()
    IMG = GROUND_IMG

    def __init__(self, y):
        """
        Initialize the object
        :param y: y coordinate of the ground
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        Moves the base left
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, window):
        """
        Draws the base
        :param window: window object
        :return: None
        """
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))


class Bird:
    VEL = 10
    IMGS = BIRD_IMGS
    ANIMATION_TIME = 10
    POSSIBLE_Y = [280, 200, 100]

    def __init__(self, x):
        self.x = x
        self.img = self.IMGS[0]
        self.y = self.POSSIBLE_Y[random.randrange(0, 3)]
        self.img_count = 0

    def move(self):
        self.x -= self.VEL

    def draw(self, window):
        self.img_count += 1

        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 2 + 1:
            # self.img = self.img[0]
            self.img_count = 0

        window.blit(self.img, (self.x, self.y))

    def collide(self, dino):
        dino_mask = dino.get_mask()
        mask = pygame.mask.from_surface(self.img)

        offset = (self.x - dino.x, self.y - round(dino.y))
        point = dino_mask.overlap(mask, offset)

        if point:
            return True
        return False


class Cactus:
    VEL = 10
    IMGS = CACTUS_IMGS

    def __init__(self, x):
        self.x = x
        self.img = self.IMGS[random.randrange(0, 3)]
        self.y = GROUND_Y - self.img.get_height() + 13

    def move(self):
        self.x -= self.VEL

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def collide(self, dino):
        dino_mask = dino.get_mask()
        mask = pygame.mask.from_surface(self.img)

        offset = (self.x - dino.x, self.y - round(dino.y))
        point = dino_mask.overlap(mask, offset)

        if point:
            return True
        return False


def draw_window(window, dinos, ground, object_arr, user_score):
    window.blit(BG_IMG, (0, 0))

    text = STAT_FONT.render("Score: " + str(user_score), 1, SCORE_FONT_COLOR)
    window.blit(text, ((WINDOW_WIDTH - 10 - text.get_width()), 10))
    text = STAT_FONT.render("Max: " + str(MAX_SCORE), 1, SCORE_FONT_COLOR)
    window.blit(text, ((WINDOW_WIDTH - 10 - text.get_width()), 70))

    text = STAT_FONT.render("Gen: " + str(GEN_NUM), 1, GENERATION_FONT_COLOR)
    window.blit(text, (10, 10))
    text = STAT_FONT.render("Live dinos: " + str(len(dinos)), 1, DINO_COUNT_FONT_COLOR)
    window.blit(text, (10, 70))

    for cactus in object_arr:
        cactus.draw(window)

    for dino in dinos:
        dino.draw(window)

    ground.draw(window)
    pygame.display.update()


def main(genomes, config):
    global GEN_NUM, MAX_SCORE, MAX_VEL
    user_score = 1

    curr_vel = 10

    nets = []
    gens = []
    dinos = []

    # get the genomes
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        dinos.append(Dino(10, GROUND_Y - DINO_RUN_IMGS[0].get_height() + 15))
        g.fitness = 0
        gens.append(g)

    base = Base(GROUND_Y)
    objects = [Cactus(WINDOW_WIDTH + 100)]

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    cnt = 0

    run_flag = True
    while run_flag:
        clock.tick(300)
        cnt += 1

        if curr_vel > MAX_VEL:
            MAX_VEL = curr_vel
        if cnt % 3 == 0:
            user_score += 1
            if user_score > MAX_SCORE:
                MAX_SCORE = user_score

        # stop condition
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_frag = False
                pygame.quit()
                quit()

        obj_index = 0
        if len(dinos):
            for i, obj in enumerate(objects):
                if obj.x > (dinos[0].x + dinos[0].img.get_width()):
                    obj_index = i
                    break
        else:
            run_flag = False
            break

        for i, dino in enumerate(dinos):
            dino.move()
            gens[i].fitness += 0.1

            bird_y = None
            if type(objects[obj_index] == Bird):
                bird_y = objects[obj_index].y

            output = nets[i].activate((abs(dino.x - objects[obj_index].x), objects[obj_index].img.get_height(),
                                       objects[obj_index].img.get_width(), bird_y))

            if output[0] > 0.5:
                dino.jump()
            elif output[1] > 0.5:
                dino.duck()

        # if user_score % 100 == 0:
        #     curr_vel += 0.4

        if cnt % 100 == 0:
            choice = random.randrange(0, 2)
            curr_vel = int(curr_vel)
            if choice == 0:
                new_cactus = Cactus(3 * 30 * curr_vel)
                new_cactus.VEL = curr_vel
                objects.append(new_cactus)
            elif choice == 1:
                new_bird = Bird(3 * 30 * curr_vel)
                new_bird.VEL = curr_vel
                objects.append(new_bird)
            base.VEL = curr_vel

        for obj in objects:
            for i, dino in enumerate(dinos):
                if obj.collide(dino):
                    gens[i].fitness -= 1
                    dinos.pop(i)
                    nets.pop(i)
                    gens.pop(i)

            obj.move()
            if obj.x < (0 - obj.img.get_width()) and len(objects) > 1:
                objects.remove(obj)

        base.move()
        draw_window(window, dinos, base, objects, user_score)
    GEN_NUM += 1


def run(config_file_path):
    """
       Main function for NEAT-NN
       :param config_file_path: path to a config file
       :return: None
       """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    statistics = neat.StatisticsReporter()
    population.add_reporter(statistics)

    try:
        winner = population.run(main, 2000)
    except pygame.error as e:
        pass
    with open("results.txt", "a+") as results_file:
        results_file.write(f"Date: {datetime.datetime.now().ctime()} \n")
        results_file.write(f"Generations: {GEN_NUM}\n")
        results_file.write(f"Speed: {MAX_VEL}\n")
        results_file.write(f"Max score: {MAX_SCORE}\n")
        results_file.write(f"\n")


if __name__ == '__main__':
    # get the path to a config file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")

    # run the NN and th game
    run(config_path)
