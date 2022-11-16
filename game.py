from hashlib import new
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 18)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

COLOR_TEXT = (0, 0, 0)
COLOR_FOOD = (255, 136, 62)
COLOR_SNAKE_IN = (41, 248, 255)
COLOR_SNAKE_OUT = (184, 253, 255)
COLOR_HEAD_IN = (255, 41, 248)
COLOR_HEAD_OUT = (255, 184, 253)
COLOR_BG = (240, 255, 171)
COLOR_BOUNDARY = (180, 175, 111)

BLOCK_SIZE = 20
BOUNDARY_SIZE = 20
SPEED = 1000

REWARD = 10
PUNISHMENT = -10

class SnakeGameAI:
    best_score = 0

    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        # init display
        self.display = pygame.display.set_mode((self.width + BOUNDARY_SIZE, self.height + BOUNDARY_SIZE))
        pygame.display.set_caption('Snake Game With Reinforcement Learning')
        self.clock = pygame.time.Clock()
        self.reset()
        
    def reset(self):
        self.direction = Direction.RIGHT
        
        self.head = Point(self.width/2, self.height/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.food_score = 0
        self.food = None
        self._place_food()
        self.movement_count = 0

    def _place_food(self):
        x = random.randint(1, (self.width-(BLOCK_SIZE + BOUNDARY_SIZE))//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(1, (self.height-(BLOCK_SIZE + BOUNDARY_SIZE))//BLOCK_SIZE)*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
        
    def play_step(self, action):
        self.movement_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._move(action)
        self.snake.insert(0, self.head)
        
        game_over = False
        if self.is_collision() or self.movement_count > 100*len(self.snake):
            game_over = True
            reinforcement_score = PUNISHMENT
            return reinforcement_score, game_over, self.food_score
            
        if self.head == self.food:
            self.food_score += 1
            reinforcement_score = REWARD
            self._place_food()
        else:
            reinforcement_score = 0
            self.snake.pop()
        
        self._update_ui()
        self.clock.tick(SPEED)
        
        return reinforcement_score, game_over, self.food_score
    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
            
        if pt.x > self.width - (BOUNDARY_SIZE) or pt.x < BOUNDARY_SIZE or pt.y > self.height - (BOUNDARY_SIZE) or pt.y < BOUNDARY_SIZE:
            return True

        if pt in self.snake[1:]:
            return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(COLOR_BG)
        
        for pt in self.snake:
            if (pt.x == self.head.x and pt.y == self.head.y):
                pygame.draw.rect(self.display, COLOR_HEAD_IN, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(self.display, COLOR_HEAD_OUT, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
            else:
                pygame.draw.rect(self.display, COLOR_SNAKE_IN, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(self.display, COLOR_SNAKE_OUT, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
            
        circle_radius=BLOCK_SIZE//2
        pygame.draw.circle(self.display, COLOR_FOOD, Point(self.food.x + circle_radius, self.food.y + circle_radius), circle_radius)

        i = 0
        while i <= ((self.height / 20)):
            x = self.width
            y = i*BLOCK_SIZE
            pygame.draw.rect(self.display, COLOR_BOUNDARY, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))
            x = 0
            pygame.draw.rect(self.display, COLOR_BOUNDARY, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))
            i += 1

        i = 0
        while i <= ((self.width / 20)):
            x = i*BLOCK_SIZE
            y = self.height
            pygame.draw.rect(self.display, COLOR_BOUNDARY, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))
            y = 0
            pygame.draw.rect(self.display, COLOR_BOUNDARY, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))
            i += 1

        self._update_text()
        pygame.display.flip()
        
    def _update_text(self):
        text = font.render("Best Score: " + str(self.best_score), True, COLOR_TEXT)
        self.display.blit(text, [0, 0*BLOCK_SIZE])
        text = font.render("Current Score: " + str(self.food_score), True, COLOR_TEXT)
        self.display.blit(text, [0, 1*BLOCK_SIZE])
        text = font.render("Movement Count: " + str(self.movement_count), True, COLOR_TEXT)
        self.display.blit(text, [0, 2*BLOCK_SIZE])

    def _move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_direction = clock_wise[index]
        elif np.array_equal(action, [0, 1, 0]):
            new_direction = clock_wise[(index + 1) % 4]
        else:
            new_direction = clock_wise[(index - 1) % 4]

        self.direction = new_direction

        x = self.head.x
        y = self.head.y

        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)
