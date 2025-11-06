import random
import pygame
import pygame_gui


pygame.init()
font = pygame.font.SysFont(None, 24) 

#Grid Parameters
DEPTH = 15
WIDTH = 30
CELL_SIZE = 50
WINDOW_SIZE = (WIDTH*CELL_SIZE + 1, DEPTH*CELL_SIZE + 175)

GRID_TOGGLE = True
PAUSE_TOGGLE = False


#Timing controls
EATING_TIME = 20

SIM_SPEED = 3000
OTTER_TIMING = 10000
URCHIN_TIMING = 5000

sim_accumulator = 0
otter_accumulator = 0
urchin_accumulator = 0

screen = pygame.display.set_mode(WINDOW_SIZE)


#Grid tile class
class Tile:
    def __init__(self, x, y, terrain):
        self.x = x
        self.y = y
        self.terrain = terrain
        self.organism = None
    def add_organism(self, organism):
        self.organism = organism
    def remove_organism(self):
        self.organism = None
    def is_empty(self):
        return self.organism == None

#Initialize Grid
grid = []
grid = [[Tile(x, y, "water") for y in range(DEPTH)] for x in range(WIDTH)]
for i in range(WIDTH):
    grid[i][DEPTH-1].terrain = "stone"


#load sprites
otter_sprite = pygame.image.load("assets/sprites/otter.png")
urchin_sprite = pygame.image.load("assets/sprites/sea-urchin.png")

#resize sprites
otter_sprite = pygame.transform.scale(otter_sprite, (CELL_SIZE, CELL_SIZE))
urchin_sprite = pygame.transform.scale(urchin_sprite, (CELL_SIZE, CELL_SIZE))

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
        #number of updates needed to finish eating (1-5)
        self.eating_time = EATING_TIME
        self.damage = random.randrange(1,5)
        #predator escape rate (0-75)
        self.luck  = random.randrange(75)
        #hunger depletion rate (1-100)
        self.endurance = random.randrange(1,100)
        self.hunger = 100
        self.inventory = "prey"
        self.rect = self.sprite.get_rect(topleft=(self.x * CELL_SIZE, self.y * CELL_SIZE))
        self.state = "move"

    def move(self, width, depth, grid):
        #generate movement direction
        dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1), (0,0)])
        newx = max(0, min(width-1, self.x + dx))
        newy = max(0, min(depth-1, self.y + dy))
        #harvest if chosen tile has prey
        if grid[newx][newy].organism.__class__ == Prey:
            self.inventory = "prey"
            grid[newx][newy].organism.lifespan = 0
            grid[newx][newy].organism = None
        #check if chosen tile is empty
        if grid[newx][newy].organism == None:
            #clear current tile
            grid[self.x][self.y].organism = None
            #update position
            self.x = newx
            self.y = newy
            self.rect = self.sprite.get_rect(topleft=(newx * CELL_SIZE, newy * CELL_SIZE))
            #set new tile's organism to self
            grid[self.x][self.y].organism = self

    def update(self):
        #state logic
        if(self.inventory == "prey" and self.y == 0):
            self.state = "eating"
        if(self.state == "eating"):
            self.eating_time -= self.damage
            if self.eating_time == 0:
                self.state = "move"
                self.inventory = "empty"
                self.hunger +=20
                self.eating_time == EATING_TIME
        else:
            self.move(WIDTH, DEPTH, grid)
        


#Prey class
class Prey:
    def __init__(self, x, y, life_span):
        self.x, self.y, self.lifespan = x, y, life_span
        self.sprite = urchin_sprite
        self.rect = self.sprite.get_rect(topleft=(self.x*CELL_SIZE, self.y*CELL_SIZE))

#list of organisms
otter_list = []
prey_list = [] 




#GUI
manager = pygame_gui.UIManager(WINDOW_SIZE)

gridlines_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, DEPTH*CELL_SIZE), (100, 50)),
                                             text='Grid Lines',
                                             manager=manager)

pause_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((101, DEPTH*CELL_SIZE), (100, 50)),
                                             text='Pause',
                                             manager=manager)

selected_organism = None

#lifespan tick function
def decrease_lifespan(organism_list):
    temp_list = []
    for o in organism_list:
        o.lifespan-=1
        if o.lifespan <= 0:
            grid[o.x][o.y].organism = None
        if o.lifespan > 0:
            temp_list.append(o)
    return temp_list


def update_sim(otter_list, prey_list):
    #update movements and hunger
    for o in otter_list:
        o.hunger-= (3 + 3/o.endurance)
        if o.hunger<= 0:
            o.lifespan = 0
        o.update()

    #update lifespans
    otter_list = decrease_lifespan(otter_list)
    prey_list = decrease_lifespan(prey_list)

    return otter_list, prey_list


def spawn_otter(otter_list, grid):
    spawn_x = random.randrange(WIDTH-1)
    spawn_y = random.randrange(5)
    OTTER_LIFESPAN = 100
    if grid[spawn_x][spawn_y].organism == None:
        print("spawning otter")
        new_otter = Otter(spawn_x, spawn_y, OTTER_LIFESPAN)
        otter_list.append(new_otter)
        grid[spawn_x][spawn_y].organism = new_otter
        

def spawn_urchin(prey_list):
    #spawn urchin
    spawn_x = random.randrange(WIDTH)
    spawn_y = DEPTH-1
    URCHIN_LIFESPAN = 100
    if not any(p.x == spawn_x for p in prey_list):
        print("spawning urchin")
        new_prey = Prey(spawn_x, spawn_y, URCHIN_LIFESPAN)
        prey_list.append(new_prey)
        grid[spawn_x][spawn_y].organism = new_prey
    


clock = pygame.time.Clock()
running = True
while running:
    #timing controls
    time_delta = clock.tick(60)/1000.0
    if PAUSE_TOGGLE:
        time_delta = 0
    sim_accumulator += time_delta * 1000
    otter_accumulator += time_delta * 1000
    urchin_accumulator += time_delta * 1000

    #event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            grid_x = mx // CELL_SIZE
            grid_y = my // CELL_SIZE
            print(grid_x, grid_y)
            if grid_y < DEPTH:
                tile = grid[grid_x][grid_y]
                if not tile.is_empty():
                    selected_organism = tile.organism
                else:
                    print("empty tile")

        #GUI handling
        manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if hasattr(event, "ui_element"):
                if event.ui_element == gridlines_button:
                    GRID_TOGGLE =  not GRID_TOGGLE
                    print("gridlines = " + str(GRID_TOGGLE))
                elif  event.ui_element == pause_button:
                    PAUSE_TOGGLE = not PAUSE_TOGGLE
                    print("pause = " + str(PAUSE_TOGGLE))
            
        
    if sim_accumulator >= SIM_SPEED:
        sim_accumulator -= SIM_SPEED
        otter_list, prey_list = update_sim(otter_list, prey_list)

    if otter_accumulator >= OTTER_TIMING:
        otter_accumulator -= OTTER_TIMING
        spawn_otter(otter_list, grid)

    if urchin_accumulator >= URCHIN_TIMING:
        urchin_accumulator -= URCHIN_TIMING
        spawn_urchin(prey_list)

    
    manager.update(time_delta)

    # Draw
    screen.fill((0, 0, 0))
    #draw grid
    for y in range(DEPTH):
        for x in range(WIDTH):
            if grid[x][y].terrain == "water":
                color = (97, 121, 161)
            elif grid[x][y].terrain == "stone":
                color = (107, 107, 107)
            pygame.draw.rect(screen, color, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), width = 0)

    #draw otters
    for o in otter_list:
        screen.blit(o.sprite, (o.x*CELL_SIZE, o.y*CELL_SIZE))

    #draw spawned prey
    for p in prey_list:
        screen.blit(p.sprite, (p.x*CELL_SIZE, p.y*CELL_SIZE))

    #draw gridlines
    if(GRID_TOGGLE):
        for i in range(DEPTH):
            pygame.draw.line(screen, (0, 0, 0), (0,i*CELL_SIZE), (WIDTH*CELL_SIZE, i*CELL_SIZE))
        for i in range(WIDTH):
            pygame.draw.line(screen, (0, 0, 0), (i*CELL_SIZE, 0), (i*CELL_SIZE, DEPTH*CELL_SIZE))


    #status rendering
    info_y = DEPTH*CELL_SIZE + 1
    if selected_organism.__class__ == Otter:
        info = [
            f"Otter ({selected_organism.x}, {selected_organism.y})",
            f"Damage: {selected_organism.damage}",
            f"Lifespan: {selected_organism.lifespan}",
            f"Hunger: {round(selected_organism.hunger,4)}",
            f"Luck: {selected_organism.luck}",
            f"Endurance: {selected_organism.endurance}",
            f"Inventory: {selected_organism.inventory}"
        ]
    elif selected_organism.__class__ == Prey:
        info = [
            f"Urchin ({selected_organism.x}, {selected_organism.y})",
            f"Lifespan: {selected_organism.lifespan}"
        ]
    if selected_organism == None or selected_organism.lifespan<=0:
        info = ["No selection"]
    for i, line in enumerate(info):
        text = font.render(line, True, (255,255,255))
        screen.blit(text, (300, info_y + i*25))

    #selection outline
    if selected_organism and selected_organism.lifespan>0:
        pygame.draw.rect(screen, (255, 255, 0), selected_organism.rect, 2)
    
    #draw GUI 
    manager.draw_ui(screen)

    pygame.display.flip()