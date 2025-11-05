import random
import pygame
import pygame_gui


pygame.init()

#Grid Parameters
DEPTH = 15
WIDTH = 30
CELL_SIZE = 50
GRID_TOGGLE = True
PAUSE_TOGGLE = False
WINDOW_SIZE = (WIDTH*CELL_SIZE + 1, DEPTH*CELL_SIZE + 100)


screen = pygame.display.set_mode(WINDOW_SIZE)

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

#Otter class
class Otter:
    def __init__(self, x, y, life_span):
        self.x, self.y, self.lifespan = x, y, life_span
        #unique color tint
        self.tint = (random.randrange(255), random.randrange(255), random.randrange(255))
        self.sprite = tint_image(otter_sprite, self.tint)
        #number of updates needed to finish eating (1-5)
        self.damage = random.randrange(5)
        #predator escape rate (0-75)
        self.luck  = random.randrange(75)
        #hunger depletion rate (1-100)
        self.endurance = random.randrange(1,100)
        self.hunger = 100

    def move(self, width, depth, grid):
        dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1), (0,0)])
        grid[self.x][self.y].organism = None
        self.x = max(0, min(width-1, self.x + dx))
        self.y = max(0, min(depth-1, self.y + dy))
        grid[self.x][self.y].organism = self

#Prey class
class Prey:
    def __init__(self, x, y, life_span):
        self.x, self.y, self.lifespan = x, y, life_span

#list of organisms
otter_list = []
prey_list = [] 

SIM_SPEED = 3000
OTTER_TIMING = 5000
URCHIN_TIMING = 3000

sim_accumulator = 0
otter_accumulator = 0
urchin_accumulator = 0

#Initialize Grid
grid = []
grid = [[Tile(x, y, "water") for y in range(DEPTH)] for x in range(WIDTH)]
for i in range(WIDTH):
    grid[i][DEPTH-1].terrain = "stone"

#GUI
manager = pygame_gui.UIManager(WINDOW_SIZE)

gridlines_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, DEPTH*CELL_SIZE), (100, 50)),
                                             text='Grid Lines',
                                             manager=manager)

pause_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((101, DEPTH*CELL_SIZE), (100, 50)),
                                             text='Pause',
                                             manager=manager)


#lifespan tick function
def decrease_lifespan(organism_list):
    temp_list = []
    for o in organism_list:
        o.lifespan-=1
        if o.lifespan > 0:
            temp_list.append(o)
    return temp_list


def update_sim(otter_list, prey_list):
    #update movements and hunger
    for o in otter_list:
        o.hunger-= (3 + 3/o.endurance)
        if o.hunger<= 0:
            o.lifespan = 0
        o.move(WIDTH, DEPTH, grid)

    #update lifespans
    otter_list = decrease_lifespan(otter_list)
    prey_list = decrease_lifespan(prey_list)


def spawn_otter(otter_list, grid):
    print("spawning otter")
    spawn_x = random.randrange(WIDTH-1)
    spawn_y = random.randrange(5)
    if grid[spawn_x][spawn_y].organism == None:
        new_otter = Otter(spawn_x, spawn_y, 100.0)
        otter_list.append(new_otter)
        grid[spawn_x][spawn_y].organism = new_otter

def spawn_urchin(prey_list):
    #spawn urchin
    print("spawning urchin")
    spawn_x = random.randrange(WIDTH)
    if not any(p.x == spawn_x for p in prey_list):
        prey_list.append(Prey(spawn_x, DEPTH-1, 100))
    


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
                    print("Selected otter:", tile.organism.hunger)
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
        update_sim(otter_list, prey_list)

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
        screen.blit(urchin_sprite, (p.x*CELL_SIZE, p.y*CELL_SIZE))

    if(GRID_TOGGLE):
        for i in range(DEPTH):
            pygame.draw.line(screen, (0, 0, 0), (0,i*CELL_SIZE), (WIDTH*CELL_SIZE, i*CELL_SIZE))
        for i in range(WIDTH):
            pygame.draw.line(screen, (0, 0, 0), (i*CELL_SIZE, 0), (i*CELL_SIZE, DEPTH*CELL_SIZE))

    #draw GUI
    manager.draw_ui(screen)

    pygame.display.flip()