from hashlib import new
from font import cfont
from direction import Direction
from collections import namedtuple

import pygame
import random
import numpy as np
import color

Grid = namedtuple('Grid', 'x, y')     #Tuple to control grids in canvas.
GRID_SIZE = 20     #Size of each grid.
BOUNDARY_SIZE = 20      #Size of the boundaries on the edge of the canvas.

SPEED = 1000    #How fast game loops iterates.

REWARD = 10     #Reward points for reinforcement learning when snake gets the food.
PUNISHMENT = -10    #Punishment points for reinforcement learning when snake dies

class SnakeGameAI:
    best_score = 0      #UI element.
    iteration = 0       #UI element.

    def __init__(self, width=640, height=480):
        self.width = width      #Size of the map.
        self.height = height
        # init display
        self.display = pygame.display.set_mode((self.width + BOUNDARY_SIZE, self.height + BOUNDARY_SIZE))       #Size of the canvas.
        pygame.display.set_caption('Snake Game With Reinforcement Learning')        #Name of the application.
        self.clock = pygame.time.Clock()
        self.reset()
        
    def reset(self):
        self.direction = Direction.RIGHT    #Default starting direction.
        
        self.head = Grid(self.width/2, self.height/2)  #Starting position of the snake with length 3.
        self.snake = [self.head, 
                      Grid(self.head.x-GRID_SIZE, self.head.y),
                      Grid(self.head.x-(2*GRID_SIZE), self.head.y)]
        
        self.food_score = 0     #Resetting score value.
        self.food = None
        self.spawn_food()      #Placing the first food onto the canvas.
        self.movement_count = 0     #Resetting the movement counter.

    def spawn_food(self):      #Finds a place for food and spawns it.
        x = random.randint(1, (self.width-(GRID_SIZE + BOUNDARY_SIZE))//GRID_SIZE)*GRID_SIZE
        y = random.randint(1, (self.height-(GRID_SIZE + BOUNDARY_SIZE))//GRID_SIZE)*GRID_SIZE
        self.food = Grid(x, y)
        if self.food in self.snake:     #If the position on snake find somewhere else.
            self.spawn_food()
        
    def play_step(self, action):    #Executed computer's choices.
        self.movement_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._move(action)
        self.snake.insert(0, self.head)
        
        game_over = False
        if self.is_collision() or self.movement_count > 100*len(self.snake):        #In the event of snake dies.
            game_over = True
            reinforcement_score = PUNISHMENT
            return reinforcement_score, game_over, self.food_score
            
        if self.head == self.food:      #In the event of snake gets the food.
            self.food_score += 1
            reinforcement_score = REWARD
            self.spawn_food()
        else:               #In the event of snake moves.
            reinforcement_score = 0
            self.snake.pop()
        
        self._update_ui()
        self.clock.tick(SPEED)
        
        return reinforcement_score, game_over, self.food_score
    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
            
        if pt.x > self.width - (BOUNDARY_SIZE) or pt.x < BOUNDARY_SIZE or pt.y > self.height - (BOUNDARY_SIZE) or pt.y < BOUNDARY_SIZE:     #In case of snake collides with boundaries.
            return True

        if pt in self.snake[1:]:        #In case of snake collides with itself.
            return True
        
        # TODO:Add Path finding here!

        return False
        
    def _update_ui(self):
        self.display.fill(color.BG)
        
        for pt in self.snake:
            if (pt.x == self.head.x and pt.y == self.head.y):       #Draws the head of the snake.
                pygame.draw.rect(self.display, color.HEAD_IN, pygame.Rect(pt.x, pt.y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(self.display, color.HEAD_OUT, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
            else:           #Draws the body of the snake.
                pygame.draw.rect(self.display, color.SNAKE_IN, pygame.Rect(pt.x, pt.y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(self.display, color.SNAKE_OUT, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
            
        circle_radius=GRID_SIZE//2
        pygame.draw.circle(self.display, color.FOOD, Grid(self.food.x + circle_radius, self.food.y + circle_radius), circle_radius)    #Draws the food.

        i = 0
        while i <= ((self.height / 20)):    #Draws the boundaries of the map.
            x = self.width
            y = i*GRID_SIZE
            pygame.draw.rect(self.display, color.BOUNDARY, pygame.Rect(x, y, GRID_SIZE, GRID_SIZE))
            x = 0
            pygame.draw.rect(self.display, color.BOUNDARY, pygame.Rect(x, y, GRID_SIZE, GRID_SIZE))
            i += 1

        i = 0
        while i <= ((self.width / 20)):     #Draws the boundaries of the map.
            x = i*GRID_SIZE
            y = self.height
            pygame.draw.rect(self.display, color.BOUNDARY, pygame.Rect(x, y, GRID_SIZE, GRID_SIZE))
            y = 0
            pygame.draw.rect(self.display, color.BOUNDARY, pygame.Rect(x, y, GRID_SIZE, GRID_SIZE))
            i += 1

        self._update_text()
        pygame.display.flip()
        
    def _update_text(self):     #Updates the game indicators.
        text = cfont.render("Iteration: " + str(self.iteration), True, color.TEXT)
        self.display.blit(text, [0, 0*GRID_SIZE])
        text = cfont.render("Best Score: " + str(self.best_score), True, color.TEXT)
        self.display.blit(text, [0, 1*GRID_SIZE])
        text = cfont.render("Current Score: " + str(self.food_score), True, color.TEXT)
        self.display.blit(text, [0, 2*GRID_SIZE])
        text = cfont.render("Movement Count: " + str(self.movement_count), True, color.TEXT)
        self.display.blit(text, [0, 3*GRID_SIZE])

    def _move(self, action):    #Moves the snake regarding to the action sent from agent.
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]    #For calculating the next direction after each action sent.
        index = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):   #Move straight command
            new_direction = clock_wise[index]
        elif np.array_equal(action, [0, 1, 0]):     #Turn right command
            new_direction = clock_wise[(index + 1) % 4]
        else:       #Turn left command
            new_direction = clock_wise[(index - 1) % 4]

        self.direction = new_direction

        x = self.head.x     #Relocates the snake with respect to the current direction.
        y = self.head.y

        if self.direction == Direction.RIGHT:
            x += GRID_SIZE
        elif self.direction == Direction.LEFT:
            x -= GRID_SIZE
        elif self.direction == Direction.DOWN:
            y += GRID_SIZE
        elif self.direction == Direction.UP:
            y -= GRID_SIZE
            
        self.head = Grid(x, y)
