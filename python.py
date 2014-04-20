import sys
import pygame
from types import *
import random
import requests

pygame.init()

random.seed()

SCREEN_SIZE = 800
FRAMES_PS = 30
STARTING_LOCATION = (0, 0)
STARTING_URL = "http://jobs.happier.com/1111"

class Cell(object):
    def __init__(self, url):
        self.url   = url
        self.lion  = False
        self.walls = {}

    def setLion(self, d):
        if "lion" in d:
            self.lion = True
            return True
        return False

    def setWalls(self, d):
        for direction in ["north", "east", "south", "west"]:
            self.walls[direction] = d.get(direction, False)

    def update(self, bad_locations):
        try:
            r = requests.get(self.url)
            d = r.json()
        except:
            print("Broken URL! ", self.url)
            d = {}

        self.setWalls(d)
        if self.setLion(d.get("goal", "")):
            return ("lion", Cell(""))

        direction = self.determineNextDirection(d, bad_locations)

        return (direction,Cell(d.get(direction, "")))

    def determineNextDirection(self, data, bad_locations):
        goal = data.get("goal", None)

        if not goal:
            return ""

        for direction in ["north", "east", "south", "west"]:
            url = data.get(direction, False)
            if (direction in goal) and url:
                if url in bad_locations:
                    print("Bad location")
                    continue
                return direction

        for direction in ["north", "east", "south", "west"]:
            url = data.get(direction, False)
            if url:
                if url in bad_locations:
                    print("Another bad location")
                    continue
                return direction

        return ""

    def display(self, unit_size, current_location=False):
        botX = unit_size
        botY = unit_size

        topLeft  = (0, 0)
        topRight = (botX, 0)
        botLeft  = (0, botY)
        botRight = (botX, botY)

        surface = pygame.Surface((unit_size, unit_size))
        self.displayLion(surface)
        self.displayWalls(surface)
        if current_location:
            self.displayCurrentLocation(surface)

        return surface

    def displayWalls(self, surface):
        topLeft  = (0, 0)
        topRight = (surface.get_width()-1 , 0)
        botLeft  = (0, surface.get_height()-1)
        botRight = (surface.get_width()-1, surface.get_height()-1)

        if self.walls.get('north', False):
            pygame.draw.line(surface, (220,220,220), topLeft, topRight)
        if self.walls.get('east', False):
            pygame.draw.line(surface, (220,220,220), topRight, botRight)
        if self.walls.get('south', False):
            pygame.draw.line(surface, (220,220,220), botLeft, botRight)
        if self.walls.get('west', False):
            pygame.draw.line(surface, (220,220,220), topLeft, botLeft)

    def displayCurrentLocation(self, surface):
        leftMiddle  = (0, surface.get_height() / 2)
        rightMiddle = (surface.get_width() - 1, surface.get_height() / 2)
        topMiddle   = (surface.get_width() / 2, 0)
        botMiddle   = (surface.get_width() / 2, surface.get_height() - 1)

        pygame.draw.line(surface, (0,255,0), leftMiddle, rightMiddle)
        pygame.draw.line(surface, (0,255,0), topMiddle,  botMiddle)

    def displayLion(self, surface):
        topLeft  = (0, 0)
        topRight = (surface.get_width() , 0)
        botLeft  = (0, surface.get_height())
        botRight = (surface.get_width(), surface.get_height())

        if self.lion:
            pygame.draw.line(surface, (255,0,0), topLeft, botRight)
            pygame.draw.line(surface, (255,0,0), topRight, botLeft)
    
class World(object):
    def __init__(self, args={}):
        self.size = (SCREEN_SIZE, SCREEN_SIZE)
        
        self.screen            = pygame.display.set_mode(self.size)
        self.previous_location = []
        self.current_location  = STARTING_LOCATION
        self.max_coordinate    = 1
        self.min_coordinate    = 0
        self.bad_locations     = []
        self.started           = False

        self.cells = {
            STARTING_LOCATION: Cell(STARTING_URL)
        }

        self.clock = pygame.time.Clock()
        self.debug = True if len(args) > 1 and args[1] == 'debug' else False

        if self.debug:
            self.initialValues()

    def initialValues(self):
        self.cells.update({
            (0,0): Cell(STARTING_URL),
            (1,0): Cell(STARTING_URL),
            (0,1): Cell(STARTING_URL),
            (2,0): Cell(STARTING_URL),
            (9,0): Cell(STARTING_URL),
            (2,2): Cell(STARTING_URL) 
        })

        self.cells[(2,0)].setLion("lion")
        self.cells[(1,0)].setWalls({"north":True})

        self.max_coordinate = 9
        self.min_coordinate = 0
        
    def run(self):
        while 1:
            self.display()

            bad_locations = list(set([self.cells[x].url for x in self.bad_locations] + [self.cells[x].url for x in self.previous_location]))

            if not self.debug and self.started:
                updated = False
                (next_direction, next_cell) = self.cells[self.current_location].update(bad_locations)
                if next_direction == "north":
                    next_location = (self.current_location[0], self.current_location[1] + 1)
                    updated = True
                elif next_direction == "east":
                    next_location = (self.current_location[0] + 1, self.current_location[1])
                    updated = True
                elif next_direction == "south":
                    next_location = (self.current_location[0], self.current_location[1] - 1)
                    updated = True
                elif next_direction == "west":
                    next_location = (self.current_location[0] - 1, self.current_location[1])
                    updated = True
                elif next_direction == "lion":
                    updated = True
                elif next_direction == "":
                    updated = True

                if updated:
                    if next_direction == "lion":
                        print("Ugh, lion")
                        self.bad_locations.append(self.current_location)
                        self.current_location = self.previous_location.pop()
                    elif next_direction == "":
                        self.bad_locations.append(self.current_location)
                        self.current_location = self.previous_location.pop()
                    else:
                        self.previous_location.append(self.current_location)
                        if self.previous_location[-1] != next_location:
                            self.current_location  = next_location
                            self.cells[self.current_location] = next_cell
                        else:
                            print("How'd I get here?!")

                    if max(self.max_coordinate, self.current_location[0]) == self.current_location[0]:
                        self.max_coordinate = self.current_location[0]
                    if max(self.max_coordinate, self.current_location[1]) == self.current_location[1]:
                        self.max_coordinate = self.current_location[1]
                    if min(self.min_coordinate, self.current_location[0]) == self.current_location[0]:
                        self.min_coordinate = self.current_location[0]
                    if min(self.min_coordinate, self.current_location[1]) == self.current_location[1]:
                        self.min_coordinate = self.current_location[1]

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    self.started = True
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            self.clock.tick(FRAMES_PS)

    def display(self):
        self.screen.fill((255,255,255))

        for key, cell in self.cells.iteritems():
            unit_size = SCREEN_SIZE / self.worldSize()
            surface = cell.display(unit_size, key == self.current_location)
            x = unit_size * key[0] - self.min_coordinate * unit_size
            y = SCREEN_SIZE - (unit_size * (key[1] + 1) - self.min_coordinate * unit_size)
            self.screen.blit(surface, (x, y))

        pygame.display.update()

    def worldSize(self):
        return self.max_coordinate - self.min_coordinate + 1
  
world = World(sys.argv)
world.run()
