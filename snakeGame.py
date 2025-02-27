from dataclasses import dataclass
from typing import List, ClassVar
import random
import pygame


@dataclass
class Fruit:
    position: List[int]
    _color: pygame.Color

    def respawn(self, snake, x_tiles: int, y_tiles: int):
        """
        Changes position of fruit to one not occupied by snake

        :param snake: snake in current game
        :return: true if successfully changes position, false if board is full
        """
        old_pos = list(self.position)

        def good_pos(new_position: List[int]):
            for body_pos in snake.get_body():
                if body_pos == new_position:
                    return False
            if new_position == old_pos:
                return False

            return True

        new_position = [random.randrange(0, x_tiles), random.randrange(0, y_tiles)]

        while not good_pos(new_position):
            new_position[0] = random.randrange(0, x_tiles)
            new_position[1] = random.randrange(0, y_tiles)
        self.position = new_position

    def get_position(self):
        return self.position


@dataclass
class Snake:
    position: List[int]
    body: List[List[int]]
    direction: int
    change_to: int
    is_alive: bool
    color: pygame.Color
    prev_tail: List[int]
    has_grown: bool = False

    def move(self, x_tiles, y_tiles):
        if self.change_to == 3 and self.direction != 1:
            self.direction = 3
        if self.change_to == 1 and self.direction != 3:
            self.direction = 1
        if self.change_to == 2 and self.direction != 0:
            self.direction = 2
        if self.change_to == 0 and self.direction != 2:
            self.direction = 0

        #checking new position, killing snake if not safe
        new_position = [self.position[0], self.position[1]]
        if self.direction == 3:
            new_position[1] -= 1
        elif self.direction == 1:
            new_position[1] += 1
        elif self.direction == 2:
            new_position[0] -= 1
        elif self.direction == 0:
            new_position[0] += 1

        if not self.is_safe_move(new_position, x_tiles, y_tiles):
            self.is_alive = False

        # Moving the snake
        if self.is_alive:
            self.position = list(new_position)
            self.body.insert(0, list(self.position))
            self.prev_tail = self.body.pop()



    def is_at_fruit(self, fruit) -> bool:
        """
        returns whether snake is at given fruit's position

        :param fruit: fruit object in snake's game
        :return: bool
        """
        return self.position[0] == fruit.get_position()[0] and self.position[1] == fruit.get_position()[1]

    def grow(self):
        """
        grows snake by 1 tile
        :return: None
        """
        self.has_grown = True
        self.body.append(list(self.prev_tail))

    def moveRight(self):
        self.change_to = 0

    def moveDown(self):
        self.change_to = 1

    def moveLeft(self):
        self.change_to = 2

    def moveUp(self):
        self.change_to = 3

    def is_safe_move(self, new_pos: list[int], x_tiles: int, y_tiles: int) -> bool:
        """
        Returns whether the snake can move into the given position

        :param new_pos: new position snake is moving to
        :param x_tiles: width of game in tiles
        :param y_tiles: height of game in tiles
        :return: True if space is safe to move to, False otherwise
        """
        # Check if moving into body
        for block in self.body[1:]:
            if new_pos[0] == block[0] and new_pos[1] == block[1]:
                return False

        # Check if moving out of borders
        if self.position[0] < 0 or self.position[0] > x_tiles - 1:
            return False
        if self.position[1] < 0 or self.position[1] > y_tiles - 1:
            return False

        return True

    def get_position(self):
        return self.position
    def get_body(self):
        return self.body

    def get_state(self, fruit: Fruit, x_tiles: int, y_tiles: int) -> List[bool]:
        """
        Returns state of snake for input into network as list of booleans length 11
        State as follows:[
            danger exists: straight, right, left
            direction is: right, down, left, up
            food is to: right, down, left, up
        ]
        :return: List[bool]
        """

        positions = [[self.position[0]+1, self.position[1]],
                     [self.position[0], self.position[1]+1],
                     [self.position[0]-1, self.position[1]],
                     [self.position[0], self.position[1]-1]]

        new_position = [self.position[0], self.position[1]]
        if self.direction == 3:
            new_position[1] -= 1
        elif self.direction == 1:
            new_position[1] += 1
        elif self.direction == 2:
            new_position[0] -= 1
        elif self.direction == 0:
            new_position[0] += 1

        state = [
            self.is_safe_move(positions[self.direction], x_tiles, y_tiles),  # straight
            self.is_safe_move(positions[(self.direction + 1) % 4], x_tiles, y_tiles),  # right
            self.is_safe_move(positions[(self.direction - 1) % 4], x_tiles, y_tiles),  # left
            self.direction == 0, self.direction == 1, self.direction == 2, self.direction == 3,
            fruit.get_position()[0] > self.position[0], # fruit right
            fruit.get_position()[1] > self.position[1], # fruit down
            fruit.get_position()[0] < self.position[0], # fruit left
            fruit.get_position()[1] < self.position[1]  # fruit up
        ]

        return state





class SnakeGame:
    def __init__(self, x_tiles: int, y_tiles: int):
        # x_tiles and y_tiles must be at least 15
        self.x_tiles = x_tiles
        self.y_tiles = y_tiles
        self.snake: Snake = Snake([10,5], [[10, 5], [9, 5], [8, 5], [7, 5]], 0, 0, True, pygame.Color(255,255,255), [0,0])
        self.fruit: Fruit = Fruit([0,0], pygame.Color(255,255,255))
        self.fruit_spawn: bool = True
        self.score: int = 0
        self.is_alive: bool = True
        self.steps_since_eating = 0

        self.fruit.respawn(self.snake, self.x_tiles, self.y_tiles)


    def step(self):

        self.snake.move(self.x_tiles, self.y_tiles)

        # checking for infinite loops
        if self.snake.is_alive:
            self.steps_since_eating += 1

            if self.steps_since_eating > len(self.snake.get_body()) + 30:  # longer snakes get more time
                self.snake.is_alive = False

        if self.snake.is_at_fruit(self.fruit):
            self.fruit.respawn(self.snake, self.x_tiles, self.y_tiles)
            self.snake.grow()
            self.score += 1
            self.fruit_spawn = False
            self.steps_since_eating = 0


    def moveRight(self):
        self.snake.moveRight()

    def moveDown(self):
        self.snake.moveDown()

    def moveLeft(self):
        self.snake.moveLeft()

    def moveUp(self):
        self.snake.moveUp()

    def is_alive(self):
        return self.is_alive

    def get_position(self):
        pass

    def get_x_tiles(self):
        pass

    def get_y_tiles(self):
        pass

    def get_fitness(self):
        pass

    def game_over(self):
        self.is_alive = False



@dataclass
class drawnGame:
    snakeGame: SnakeGame
    game_window: pygame.display
    topLeft: tuple[int, int]
    width: int
    height: int

    def draw(self):
        """
        Draw snake game on to game_window, both stored as instance vars
        """
        green = pygame.Color(0, 255, 0)
        white = pygame.Color(255, 255, 255)
        tileGap = 0

        # drawing border
        pygame.draw.lines(self.game_window, white, True, [(self.topLeft[0], self.topLeft[1]), (self.topLeft[0] + self.width, self.topLeft[1]),
                                                     (self.topLeft[0] + self.width, self.topLeft[1] + self.width),
                                                     (self.topLeft[0], self.topLeft[1] + self.width)])


        # drawing snake
        for pos in self.snakeGame.snake.get_body():
            pygame.draw.rect(self.game_window, green,
                             pygame.Rect((pos[0] / self.snakeGame.x_tiles) * self.width + self.topLeft[0] + tileGap,
                                         (pos[1] / self.snakeGame.y_tiles) * self.height + self.topLeft[1] + tileGap,
                                         self.width // self.snakeGame.x_tiles - tileGap,
                                         self.height // self.snakeGame.y_tiles - tileGap))

        # drawing fruit
        pygame.draw.rect(self.game_window, white, pygame.Rect(
            (self.snakeGame.fruit.get_position()[0] / self.snakeGame.x_tiles) * self.width + self.topLeft[0],
            (self.snakeGame.fruit.get_position()[1] / self.snakeGame.y_tiles) * self.height + self.topLeft[1],
            self.width // self.snakeGame.x_tiles, self.height // self.snakeGame.y_tiles))



