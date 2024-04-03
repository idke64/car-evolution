import math
import random
import time
from random import randint
import numpy as np
import copy

import pygame.sprite

from objects import *

import pygame as pg
pygame.init()
WINDOW = pg.display.set_mode((990, 540))
TRACK_1 = pg.image.load('assets/track1.png').convert_alpha()
TRACK_2 = pg.image.load('assets/track2.png').convert_alpha()
TRACK_3 = pg.image.load('assets/track3.png').convert_alpha()
TRACK_4 = pg.image.load('assets/track4.png').convert_alpha()
FPS = 60
BG_COLOR = (150,150,150)
CLOCK = pg.time.Clock()


class Main:
    def __init__(self):
        self.track = pygame.sprite.Sprite()
        self.track.image = TRACK_4
        self.track.rect = self.track.image.get_rect()
        self.track.mask = pg.mask.from_surface(self.track.image)
        self.track.mask.invert()
        self.cars = []
        self.camera_car = None
        self.best_brain = None
        self.best_brain_of_batch = None
        self.best_angle = 0
        self.minimap = Minimap(self.cars)
        self.generation = 0


    def get_draw_pos(self,image,object_pos):
        new_pos = (object_pos[0] - self.camera_car.pos[0] + WINDOW.get_width() // 2 - image.get_rect().width // 2,
                   object_pos[1] - self.camera_car.pos[1] + WINDOW.get_height() // 2 - image.get_rect().height // 2)
        return new_pos


    def draw(self):
        #background
        WINDOW.fill(BG_COLOR)
        #track
        WINDOW.blit(self.track.image,self.get_draw_pos(self.track.image,[1500,1500]))

        font = pg.font.Font('freesansbold.ttf',32)
        text1 = font.render('Generation ' + str(self.generation),True,[0,255,0])
        text2 = font.render('Best Distance ' + str(int(self.best_angle)),True,[0,255,0])
        text1_rect = text1.get_rect()
        text1_rect.center = (WINDOW.get_width() // 8, WINDOW.get_height() // 2)
        text2_rect = text2.get_rect()
        text2_rect.center = (WINDOW.get_width() // 7, WINDOW.get_height() // 1.7)
        WINDOW.blit(text1,text1_rect)
        WINDOW.blit(text2, text2_rect)

        for car in self.cars:
            rotated_car = car.draw()
            new_pos_car = self.get_draw_pos(rotated_car,(car.pos[0],car.pos[1]))
            pg.draw.rect(WINDOW,[255,255,255],car.rect)
            WINDOW.blit(rotated_car, new_pos_car)

        # map
        self.minimap.draw()

        pg.display.update()

    def collision(self):
        for car in self.cars:

            car_collide = pg.sprite.collide_mask(car,self.track)
            if car_collide is not None:
                car.collide += 1

    def angle(self,car):
        a = (math.atan2(car.pos[1] - 1500, car.pos[0] - 1500)) * 360 / (2 * math.pi)
        if car.pos[1] < 1500:
            a += 360
        return a

    def spawn_cars(self,num):
        self.generation += 1
        temp = []
        for i in range(num):
            copy_of_best_brain = copy.deepcopy(self.best_brain)
            car = Car([2700, 1850], False, copy_of_best_brain)
            car.brain.mutate(10)
            temp.append(car)
        for i in range(num):
            copy_of_best_brain_batch = copy.deepcopy(self.best_brain_of_batch)
            car = Car([2700, 1850], False, copy_of_best_brain_batch)
            car.brain.mutate(10)
            temp.append(car)
        self.cars.clear()
        self.cars = temp
        self.minimap.cars = self.cars

    def run(self):
        c1 = Car([2700,1850],False)
        self.camera_car = c1
        self.spawn_cars(20)

        self.camera_car = self.cars[0]
        self.best_brain = self.camera_car.brain

      
        run = True
        events = pg.event.get()

        prev_tick = pg.time.get_ticks()


        while run:

            pg.display.set_caption('FPS: ' + str(CLOCK.get_fps()))

            events = pg.event.get()

            keys = pg.key.get_pressed()
            if keys[pg.K_w]:
                c1.accelerate(0.5)
            if keys[pg.K_s]:
                c1.accelerate(-0.5)
            if keys[pg.K_a]:
                c1.rotate(3)
            if keys[pg.K_d]:
                c1.rotate(-3)


            max_angle = 0
            best_car = self.cars[0]
            for car in self.cars:
                car.update()
                output = car.brain.feed_forward([car.pos[0],car.pos[1],car.velocity[0],car.velocity[1],car.rotation])

                car.rotate(output[1] * 1.5)
                car.accelerate(output[0] * 1.5)
                car_angle = self.angle(car)
                if car_angle > max_angle:
                    max_angle = car_angle
                    best_car = car
                
                
            self.camera_car = best_car

            self.collision()

            curr_tick = pg.time.get_ticks()

            all_stopped = True

            for car in self.cars:
                if car.collide < 2:
                    all_stopped = False
            if curr_tick - prev_tick > 7000 or all_stopped:
                cc_angle = self.angle(self.camera_car)
                if cc_angle > self.best_angle:
                    self.best_angle = cc_angle
                    self.best_brain = best_car.brain
                self.best_brain_of_batch = best_car.brain
                self.spawn_cars(20)
                prev_tick = curr_tick


            for event in events:
                if event.type == pg.QUIT:
                    run = False
                    pg.quit()
            CLOCK.tick(FPS)

            self.draw()

class NeuralNetwork():
    def __init__(self,input=5,layer1=64,output=2):

        self.input_size = input
        self.layer1_size = layer1
        self.output_size = output

        self.weight_0_1 = []
        self.bias_1 = []
        self.weight_1_2 = []
        self.bias_2 = []

        for i in range(self.layer1_size):
            weights = []
            for j in range(input):
                weights.append(random.uniform(-0.05, 0.05))
            self.weight_0_1.append(weights)
        for i in range(self.output_size):
            weights = []
            for j in range(self.layer1_size):
                weights.append(random.uniform(-0.05, 0.05))
            self.weight_1_2.append(weights)
        for i in range(self.layer1_size):
            self.bias_1.append(random.uniform(-1, 1))
        for i in range(self.output_size):
            self.bias_2.append(random.uniform(-1, 1))


    def feed_forward(self,inputs):
        layer1 = []
        for i in range(self.layer1_size):
            new_node = 0
            for j in range(self.input_size):
                new_node += inputs[j] * self.weight_0_1[i][j]
            new_node += self.bias_1[i]
            #relu
            new_node = max(0, new_node)
            layer1.append(new_node)
        output = []
        for i in range(self.output_size):
            new_node = 0
            for j in range(len(layer1)):
                new_node += layer1[j] * self.weight_1_2[i][j]
            new_node += self.bias_2[i]
            # sigmoid
            new_node = 1/(1 + np.exp(-1 * new_node))

            output.append(new_node * 3 - 1)
        return output

    def mutate(self,scale):
        for i in range(self.layer1_size):
            for j in range(self.input_size):
                self.weight_0_1[i][j] = random.uniform(self.weight_0_1[i][j]-(scale / 40),self.weight_0_1[i][j]+(scale / 40))
        for i in range(self.output_size):
            for j in range(self.layer1_size):
                self.weight_1_2[i][j] = random.uniform(self.weight_1_2[i][j]-(scale / 40),self.weight_1_2[i][j]+(scale / 40))
        for i in range(self.layer1_size):
            self.bias_1[i]  = random.uniform(self.bias_1[i]-scale,self.bias_1[i]+scale)
        for i in range(self.output_size):
            self.bias_2[i] = random.uniform(self.bias_2[i] - scale, self.bias_2[i] + scale)


if __name__ == '__main__':
    main = Main()
    main.run()
