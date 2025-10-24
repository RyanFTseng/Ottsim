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

#Prey class
class Prey:
    def __init__(self, x, y, life_span):
        self.x, self.y, self.lifespan = x, y, life_span

#list of prey
prey_list = [] 


#urchin spawn event
URCHIN_SPAWN = pygame.USEREVENT+1
pygame.time.set_timer(URCHIN_SPAWN, 3000)

#Map update event
UPDATE = pygame.USEREVENT+1
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
            #decrease lifespan
            new_prey_list = []
            for p in prey_list:
                p.lifespan -= 1
                if p.lifespan > 0:
                    new_prey_list.append(p)
            prey_list = new_prey_list
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

    #draw spawned prey
    for p in prey_list:
        print(p.x*CELL_SIZE+CELL_SIZE//2, p.y*CELL_SIZE+CELL_SIZE//2)
        pygame.draw.circle(screen, (255, 0, 255), (p.x*CELL_SIZE+CELL_SIZE//2, (p.y*CELL_SIZE+CELL_SIZE//2)-50), 10)
    
    
    pygame.display.flip()
    clock.tick(1000)