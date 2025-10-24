import random
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import pygame

#Grid Parameters
DEPTH = 15
WIDTH = 30
CELL_SIZE = 50

screen = pygame.display.set_mode((WIDTH*CELL_SIZE + 1, DEPTH*CELL_SIZE + 1))

#load sprites
otter_sprite = pygame.image.load("assets/sprites/otter.png")

#resize sprites
otter_sprite = pygame.transform.scale(otter_sprite, (CELL_SIZE, CELL_SIZE))


#Otter class
class Otter:
    def __init__(self, x, y, life_span):
        self.x, self.y, self.lifespan = x, y, life_span
        #unique color tint
        self.tint = (random.randrange(255), random.randrange(255), random.randrange(255))
        #tiles moved/update (1-5)
        self.movespeed = random.randrange(5)
        #number of updates needed to finish eating (1-5)
        self.damage = random.randrange(5)
        #predator escape rate (0-75)
        self.luck  = random.randrange(75)
        #hunger depletion rate (1-100)
        self.endurance = random.randrange(100)


#Prey class
class Prey:
    def __init__(self, x, y, life_span):
        self.x, self.y, self.lifespan = x, y, life_span

#list of organisms
otter_list = []
prey_list = [] 


#otter spawn event
OTTER_SPAWN = pygame.USEREVENT+1
pygame.time.set_timer(OTTER_SPAWN, 5000)


#urchin spawn event
URCHIN_SPAWN = pygame.USEREVENT+2
pygame.time.set_timer(URCHIN_SPAWN, 3000)


#Map update event
UPDATE = pygame.USEREVENT+3
pygame.time.set_timer(UPDATE, 1000)


clock = pygame.time.Clock()

running = True
while running:
    #event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #update 1 cycle
        if event.type == UPDATE:
            #decrease otter lifespan
            new_otter_list = []
            for o in otter_list:
                o.lifespan -= 1
                if o.lifespan > 0:
                    new_otter_list.append(o)
            otter_list = new_otter_list
            #decrease prey lifespan
            new_prey_list = []
            for p in prey_list:
                p.lifespan -= 1
                if p.lifespan > 0:
                    new_prey_list.append(p)
            prey_list = new_prey_list
        #spawn otter
        if event.type == OTTER_SPAWN:
            print("spawning otter")
            spawn_x = random.randrange(WIDTH)
            spawn_y = random.randrange(5)
            if not any(o.x == spawn_x and o.y == spawn_y for o in otter_list):
                otter_list.append(Otter(spawn_x,random.randrange(DEPTH), 10))
        #spawn urchin
        if event.type == URCHIN_SPAWN:
            print("spawning urchin")
            spawn_x = random.randrange(WIDTH)
            if not any(p.x == spawn_x for p in prey_list):
                prey_list.append(Prey(spawn_x, DEPTH, 10))


    # Draw
    screen.fill((0, 0, 0))
    #draw grid
    for y in range(DEPTH):
        for x in range(WIDTH):
            color = (32, 12, 255)
            pygame.draw.rect(screen, color, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), width = 1)


    #draw otters
    for o in otter_list:
        screen.blit(otter_sprite, (o.x*CELL_SIZE, o.y*CELL_SIZE))

    #draw spawned prey
    for p in prey_list:
        pygame.draw.circle(screen, (255, 0, 255), (p.x*CELL_SIZE+CELL_SIZE//2, (p.y*CELL_SIZE+CELL_SIZE//2)-50), 10)

    
    
    pygame.display.flip()
    clock.tick(1000)