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

def tint_image(image, tint_color):
    tinted = image.copy()
    tint_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tint_surface.fill(tint_color + (0,))  # keep alpha channel
    tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted



#Otter class
class Otter:
    def __init__(self, x, y, life_span):
        self.x, self.y, self.lifespan = x, y, life_span
        #unique color tint
        self.tint = (random.randrange(255), random.randrange(255), random.randrange(255))
        self.sprite = tint_image(otter_sprite, self.tint)
        #tiles moved/update (1-5)
        self.movespeed = random.randrange(5)
        #number of updates needed to finish eating (1-5)
        self.damage = random.randrange(5)
        #predator escape rate (0-75)
        self.luck  = random.randrange(75)
        #hunger depletion rate (1-100)
        self.endurance = random.randrange(100)

    def move(self, width, depth):
        dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1), (0,0)])
        self.x = max(0, min(width-1, self.x + dx))
        self.y = max(0, min(depth-1, self.y + dy))


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
pygame.time.set_timer(UPDATE, 500)

#lifespan tick function
def decrease_lifespan(organism_list):
    temp_list = []
    for o in organism_list:
        o.lifespan-=1
        if o.lifespan > 0:
            temp_list.append(o)
    return temp_list
    


clock = pygame.time.Clock()
running = True
while running:
    #event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #update 1 cycle
        if event.type == UPDATE:
            #update lifespans
            otter_list = decrease_lifespan(otter_list)
            prey_list = decrease_lifespan(prey_list)

            #update movements
            for o in otter_list:
                o.move(WIDTH, DEPTH)
        #spawn otter
        if event.type == OTTER_SPAWN:
            print("spawning otter")
            spawn_x = random.randrange(WIDTH)
            spawn_y = random.randrange(5)
            if not any(o.x == spawn_x and o.y == spawn_y for o in otter_list):
                otter_list.append(Otter(spawn_x,random.randrange(DEPTH), 100))
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
        screen.blit(o.sprite, (o.x*CELL_SIZE, o.y*CELL_SIZE))

    #draw spawned prey
    for p in prey_list:
        pygame.draw.circle(screen, (255, 0, 255), (p.x*CELL_SIZE+CELL_SIZE//2, (p.y*CELL_SIZE+CELL_SIZE//2)-50), 10)

    
    
    pygame.display.flip()
    clock.tick(1000)