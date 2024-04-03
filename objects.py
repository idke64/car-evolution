import pygame as pg
from main import *

CAR_MODEL = pg.image.load('assets/car.png').convert_alpha()
CAR_GREY_MODEL = pg.image.load('assets/car_transparent.png').convert_alpha()
MAP = pg.image.load('assets/track4_whole.png').convert_alpha()
RAY = pg.image.load('assets/ray.png').convert_alpha()

class Car(pygame.sprite.Sprite):
    def __init__(self,pos = [WINDOW.get_width() // 2, WINDOW.get_height() // 2],transparent = False, brain = None):
        super().__init__()
        self.transparent = transparent
        if transparent:
            self.image = CAR_GREY_MODEL
        else:
            self.image = CAR_MODEL
        self.pos = pos
        self.rect = self.image.get_rect()

        self.max_spd = 20
        self.friction = .2
        self.velocity = [0, 0]
        self.speed = 0
        self.mask = pg.mask.from_surface(self.image)
        self.collide = 0
        if brain is None:
            self.brain = NeuralNetwork()
        else:
            self.brain = brain

        self.rotation = -90
        #self.rays = [Ray(25,self.pos,self.rotation)]


    def draw(self):
        rotated_image = pg.transform.rotate(self.image, self.rotation - 90)
        self.rect = rotated_image.get_rect()
        self.rect.centerx = self.pos[0]
        self.rect.centery = self.pos[1]
        return rotated_image

    def rotate(self, angle):
        if self.collide < 2:
            self.rotation += angle
            self.rotation = self.rotation % 360

    def accelerate(self, acc):


        if abs(acc + self.speed) > self.max_spd:
            if acc + self.speed < 0:
                self.speed = -self.max_spd
            elif acc + self.speed > 0:
                self.speed = self.max_spd
        else:
            self.speed += acc

    def update(self):
        if self.collide < 2:
            self.velocity[0] = math.cos(math.radians(self.rotation)) * self.speed
            self.velocity[1] = -math.sin(math.radians(self.rotation)) * self.speed

            self.pos[0] += self.velocity[0]
            self.pos[1] += self.velocity[1]
            #for ray in self.rays:
             #   ray.pos[0] = self.pos[0] + (75 + 87//2 + 1) * math.cos(math.radians(ray.rotation + self.rotation))
             #   ray.pos[1] = self.pos[1] - (75 + 87//2 + 1) * math.sin(math.radians(ray.rotation + self.rotation))

            if abs(self.speed) <= self.friction:
                self.speed = 0
            if self.speed > 0:
                self.speed -= self.friction
            elif self.speed < 0:
                self.speed += self.friction

class Ray(pg.sprite.Sprite):
    def __init__(self,angle,car_pos,car_rotation):
        super().__init__()
        self.rotation = angle
        self.image = RAY
        self.rect = self.image.get_rect()
        self.pos = [car_pos[0] + (75 + 87//2 + 1) * math.cos(math.radians(self.rotation + car_rotation)),car_pos[1] - (75 + 87//2 + 1) * math.sin(math.radians(self.rotation + car_rotation))]
        self.mask = pg.mask.from_surface(self.image)

    def draw(self,car_rotation):
        angle = self.rotation - 90 + car_rotation
        rotated_image = pg.transform.rotate(self.image, angle)
        self.rect = rotated_image.get_rect()
        self.rect.centerx = self.pos[0]
        self.rect.centery = self.pos[1]
        pg.draw.rect(WINDOW,[255,255,255],self.rect)

        return rotated_image


class Minimap:
    def __init__(self,cars=[]):
        self.size = [200,200]
        self.pos = [20,20]
        self.image = pg.transform.scale(MAP,self.size)
        self.cars = cars

    def draw(self):
        WINDOW.blit(self.image,self.pos)

        #map cars to minimap
        for car in self.cars:
            pos = [car.pos[0] * (self.size[0] / 3000) + self.pos[0] ,car.pos[1] * (self.size[1] / 3000) + self.pos[1]]
            if pos[0] > self.pos[0] and pos[0] < self.pos[0] + self.size[0] and pos[1] > self.pos[1] and pos[1] < self.pos[1] + self.size[1]:
                pg.draw.circle(WINDOW, [255, 0, 0], pos, 3)






