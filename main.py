from snakeGame import *
import pygame
import os
import neat
import pickle

WIN_WIDTH = 1000
WIN_HEIGHT = 1000
SPEED = 4
DRAWING = True


def eval_genomes(genomes, config):
    global SPEED
    global DRAWING

    # Initializing pygame
    pygame.init()

    # Initialise game window
    pygame.display.set_caption('Snakes')
    game_window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    # FPS (frames per second) controller
    fps = pygame.time.Clock()

    nets = []
    ge = []
    snake_games = []
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        snake_games.append(SnakeGame(15, 15))
        g.fitness = 0
        ge.append(g)

    pos = [10, 10]
    drawnGames = []
    for game in snake_games:
        drawnGames.append(drawnGame(game, game_window, (pos[0], pos[1]), 100, 100))

        if pos[0] + 100 > (WIN_WIDTH - 100):
            pos[1] += 100
            pos[0] = 10
        else:
            pos[0] += 100

    # main loop
    running = True
    while running:
        game_window.fill(pygame.Color(0, 0, 0))

        # Frame Per Second /Refresh Rate
        fps.tick(SPEED)

        if len(snake_games) <= 0:
            running = False
            break

        # activating networks, sending action to snakes
        for i, g in enumerate(snake_games):
            g.step()
            genomes[i][1].fitness += .1
            output = nets[i].activate(tuple(g.snake.get_state(g.fruit, g.x_tiles, g.y_tiles)))

            max_out = -1
            max_dir = -1
            for i, n in enumerate(output):
                if n > max_out:
                    max_out = n
                    max_dir = i

            if max_dir == 0:
                g.moveRight()
            elif max_dir == 1:
                g.moveDown()
            elif max_dir == 2:
                g.moveLeft()
            elif max_dir == 3:
                g.moveUp()

        # drawing games
        if DRAWING:
            for game in drawnGames:
                game.draw()

        # penalize model for dying, reward for growing
        for i, g in enumerate(snake_games):
            if not g.snake.is_alive:
                ge[i].fitness -= 1
                snake_games.pop(i)
                nets.pop(i)
                ge.pop(i)
                drawnGames.pop(i)
            elif g.snake.has_grown:
                ge[i].fitness += 2

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    SPEED *= 2
                if event.key == pygame.K_LEFT:
                    if SPEED > 1:
                        SPEED /= 2
                if event.key == pygame.K_d:
                    DRAWING = not DRAWING

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Refresh game screen
        pygame.display.update()


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 10000)
    print(f"Saving winner as: winner.pkl")

    with open("./Models/winner.pkl", "wb") as file:
        pickle.dump(winner, file)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config_feedforward.txt")
    run(config_path)
