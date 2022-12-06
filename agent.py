import torch
import random
import numpy as np

from collections import deque
from game import SnakeGameAI, Direction, Grid, GRID_SIZE
from model import Linear_QNet, QTrainer
from graph import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(11, 256, 3)    #11 and 3 is fixed values but middle one can be changed
        self.trainer = QTrainer(self.model, lr=LEARNING_RATE, gamma=self.gamma)


    def get_state(self, game):
        head = game.snake[0]
        right_point = Grid(head.x + GRID_SIZE, head.y)
        left_point = Grid(head.x - GRID_SIZE, head.y)
        up_point = Grid(head.x, head.y - GRID_SIZE)
        down_point = Grid(head.x, head.y + GRID_SIZE)
        
        right_direction = game.direction == Direction.RIGHT
        left_direction = game.direction == Direction.LEFT
        up_direction = game.direction == Direction.UP
        down_direction = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (right_direction and game.is_not_safe(right_point)) or 
            (left_direction and game.is_not_safe(left_point)) or 
            (up_direction and game.is_not_safe(up_point)) or 
            (down_direction and game.is_not_safe(down_point)),

            # Danger right_direction
            (up_direction and game.is_not_safe(right_point)) or 
            (down_direction and game.is_not_safe(left_point)) or 
            (left_direction and game.is_not_safe(up_point)) or 
            (right_direction and game.is_not_safe(down_point)),

            # Danger left_direction
            (down_direction and game.is_not_safe(right_point)) or 
            (up_direction and game.is_not_safe(left_point)) or 
            (right_direction and game.is_not_safe(up_point)) or 
            (left_direction and game.is_not_safe(down_point)),
            
            # Move direction
            left_direction,
            right_direction,
            up_direction,
            down_direction,
            
            # Food location 
            game.food.x < game.head.x,
            game.food.x > game.head.x,
            game.food.y < game.head.y,
            game.food.y > game.head.y
            ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reinforcement_score, next_state, done):
        self.memory.append((state, action, reinforcement_score, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(np.array(states), actions, rewards, np.array(next_states), dones)

    def train_short_memory(self, state, action, reinforcement_score, next_state, done):
        self.trainer.train_step(state, action, reinforcement_score, next_state, done)

    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    plot_best_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:
        state_old = agent.get_state(game)

        final_move = agent.get_action(state_old)

        reinforcement_score, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reinforcement_score, state_new, done)

        agent.remember(state_old, final_move, reinforcement_score, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1
            game.iteration = agent.n_games
            agent.train_long_memory()

            if score > record:
                record = score
                game.best_score = record
                agent.model.save()

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot_best_scores.append(record)
            plot(plot_scores, plot_mean_scores, plot_best_scores)
