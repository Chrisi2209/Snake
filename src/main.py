from __future__ import annotations
from typing import List, Tuple, Dict, Optional, Generic, TypeVar
import os
import sys
import logging
import pygame
import random
from enum import Enum
from time import sleep
from threading import Thread


Coordinate = Tuple[int, int]
RGB = Tuple[int, int, int]
T = TypeVar("T")

def setup_logging(name: str) -> logging.Logger:
    path_to_dir: str = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs"))
    path_to_log: str = os.path.abspath(os.path.join(path_to_dir, f"{name}.log"))

    if not os.path.exists(path_to_dir):
        os.mkdir(path_to_dir)

    file_handler: logging.FileHandler = logging.FileHandler(path_to_log)    
    file_handler.setFormatter(logging.Formatter("%(levelname)-7s %(processName)s %(threadName)s %(asctime)s %(funcName)s: %(message)s"))

    logger: logging.Logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    
    return logger

def coordinate_lte(coor1: Coordinate, coor2: Coordinate):
    # y before x
    if coor1[1] < coor2[1]:
        return True
    
    if coor1[1] > coor2[1]:
        return False
    
    # if y are the same
    if coor1[0] > coor2[0]:
        return False

    return True

class direction(Enum):
    up: int = 0
    left: int = 1
    down: int = 2
    right: int = 3

class Queue(Generic[T]):
    def __init__(self, content: List[T]):
        self.container: List[T] = content

    def pop(self) -> T:
        return self.container.pop(0)
    
    def push(self, item: T) -> None:
        self.container.append(item)
    
    def __repr__(self) -> str:
        return f"<Queue {self.container}>"
    
    __str__ = __repr__
    
    def __iter__(self):
        return iter(self.container)
    
    def __len__(self) -> int:
        return len(self.container)
    
    def __contains__(self, item: T) -> bool:
        return item in self.container

class Cherry:
    def __init__(self, surface: pygame.Surface, square_length: int = 30, color: RGB = (0, 255, 0)):
        self.color = color
        self.square_length: int = square_length
        self.MAX_GRID_Y: int = surface.get_height() // self.square_length - 1
        self.MAX_GRID_X: int = surface.get_width() // self.square_length - 1 
        self.background: RGB = surface.get_at((0, 0))

        self.surface: pygame.Surface = surface
        self.position: Coordinate = None
        self.snake: Snake = None

    def set_snake(self, snake: Snake):
        self.snake = snake 
        self.new_position()
        self.draw()

    def new_position(self):
        empty_cells: int = (self.MAX_GRID_X + 1) * (self.MAX_GRID_Y + 1) - len(self.snake.snake_blocks)
        
        grid_number: int = random.randint(0, empty_cells)
        
        new_position: List[int, int] = [grid_number % (self.MAX_GRID_X + 1), grid_number // (self.MAX_GRID_Y + 1)]
                
        for block in self.snake.snake_blocks:
            if coordinate_lte(block, new_position):
                new_position[0] += 1
                if new_position[0] > self.MAX_GRID_X:
                    new_position[0] = 0
                    new_position[1] += 1

        self.position = new_position

    def eat(self):
        """
        Assumes that sprite has already been replced by snake
        """
        self.snake.grow()
        self.new_position()
        self.draw()

    def draw(self):
        pygame.draw.rect(
            self.surface, 
            self.color, 
            pygame.Rect(self.position[0] * self.square_length, 
                        self.position[1] * self.square_length, 
                        self.square_length, 
                        self.square_length
            )
        )

class Snake:
    def __init__(self, surface: pygame.Surface, cherry: Cherry, start_pos: Coordinate = (5, 7),  start_len: int = 3, 
                 start_move_direction: direction = direction.up, color: RGB = (255, 0, 0), 
                 head_color: RGB = (0, 0, 255), square_length: int = 30):
        
        self.square_length: int = square_length
        self.MAX_GRID_Y: int = surface.get_height() // self.square_length - 1
        self.MAX_GRID_X: int = surface.get_width() // self.square_length - 1 
        self.background: RGB = surface.get_at((0, 0))
        self.sprites: List[pygame.Rect] = []

        self.cherry = cherry
        self.surface: pygame.surface = surface
        self.position: Coordinate = start_pos
        self.move_direction: direction = start_move_direction
        self.length: int = start_len
        self.color: RGB = color
        self.head_color: RGB = head_color
        self.last_move: direction = direction.up

        self.snake_blocks: Queue[Coordinate] = Queue([])

        self.stop: bool = False  # for stopping the application
        self.dead: bool = False  # if you die, this will be True

    @property
    def out_of_bounds(self):
        return self.position[0] < 0 or self.position[0] > self.MAX_GRID_X or \
               self.position[1] < 0 or self.position[1] > self.MAX_GRID_Y

    def grow(self):
        self.length += 1

    def move(self):
        # update position
        self.last_move = self.move_direction

        if self.move_direction == direction.up:
            self.position = (self.position[0], self.position[1] - 1)
        
        if self.move_direction == direction.left:
            self.position = (self.position[0] - 1, self.position[1])
        
        if self.move_direction == direction.down:
            self.position = (self.position[0], self.position[1] + 1)
        
        if self.move_direction == direction.right:
            self.position = (self.position[0] + 1, self.position[1])

        if len(self.snake_blocks) > self.length - 1:
            self.snake_blocks.pop()

        # death conditions
        if self.out_of_bounds or self.position in self.snake_blocks:
            self.dead = True

        # update snake_blocks
        self.snake_blocks.push(self.position)

        # eat cherry
        if self.position[0] == self.cherry.position[0] and self.position[1] == self.cherry.position[1]:
            self.cherry.eat()


    def draw(self):
        # clear sprites from before
        if len(self.sprites) != 0:
            pygame.draw.rect(self.surface, self.background, pygame.Rect(self.sprites[0].left, self.sprites[0].top, self.sprites[0].width, self.sprites[0].height))

        self.sprites.clear()
        for coor in self.snake_blocks:
            self.sprites.append(pygame.Rect(self.square_length * coor[0], self.square_length * coor[1],
                        self.square_length, self.square_length))

        for sprite in self.sprites:
            pygame.draw.rect(self.surface, self.color, sprite)
        
        pygame.draw.rect(self.surface, self.head_color, self.sprites[-1])

    def moving_cycle(self, delay: float=0.2):
        while True:
            sleep(delay)
            
            self.move()
            if self.dead:
                return
            
            if self.stop:
                return
            
            self.draw()
    
    def exit(self):
        self.stop = True

def main():
    pygame.display.init()
    surface: pygame.Surface = pygame.display.set_mode((600, 800))
    cherry: Cherry = Cherry(surface)
    snake: Snake = Snake(surface, cherry)
    cherry.set_snake(snake)

    Thread(target=snake.moving_cycle).start()

    try:
        while True:
            for event in pygame.event.get():
                # exit
                if event.type == pygame.QUIT:
                    snake.exit()
                    pygame.quit()
                    sys.exit()

                # keypresses
                if event.type == pygame.KEYDOWN:
                    # up
                    if (event.key == pygame.K_w or event.key == pygame.K_UP) and snake.last_move != direction.down:
                        snake.move_direction = direction.up
                    # down
                    if (event.key == pygame.K_a or event.key == pygame.K_LEFT) and snake.last_move != direction.right:
                        snake.move_direction = direction.left
                    # left
                    if (event.key == pygame.K_s or event.key == pygame.K_DOWN) and snake.last_move != direction.up:
                        snake.move_direction = direction.down
                    # right
                    if (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and snake.last_move != direction.left:
                        snake.move_direction = direction.right
            
            if snake.dead:
                sys.exit()

            pygame.display.update()

    except KeyboardInterrupt:
        snake.exit()
        sys.exit()

if __name__ == "__main__":
    logger: logging.Logger = setup_logging("game")
    main()
