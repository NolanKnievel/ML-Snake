from snakeGame import *
import pygame
import os
import neat
import pickle
import neat

WIN_WIDTH = 800
WIN_HEIGHT = 800
SPEED = 8


class Connection:
    def __init__(self, input, output, weight, enabled):
        self.input = input
        self.output = output
        self.weight = weight
        self.enabled = enabled

#
# def get_model_layers(genome, config)-> List[List[int]]:
#
#     input_nodes = config.genome_config.input_keys
#     hidden_nodes = list(genome.nodes.keys())
#     output_nodes = config.genome_config.output_keys
#
#     # Collect all connections
#     connections = []
#
#     for conn_key, conn_gene in genome.connections.items():
#         connections.append(Connection(conn_key[0], conn_key[1], conn_gene.weight, conn_gene.enabled))
#
#     # assemble adjacency list of the NN graph
#     adj_list = {}
#     for i, connection in enumerate(connections):
#         if connection.input not in adj_list.keys():
#             adj_list[connection.input] = set()
#             adj_list[connection.input].add(connection.output)
#         else:
#             adj_list[connection.input].add(connection.output)
#
#     print(adj_list)
#
#     # starting at first input Node
#     start = -1
#
#     # bfs, putting nodes into list of layers
#     layers = [input_nodes]
#     queue = input_nodes.copy()
#     layer = 0
#     current = None
#     visited = set()
#     next_layer_size = 0
#
#     while queue:
#         if layer > len(layers)-1:
#             layers.append([])
#
#         if not current:
#             layer_size = 1
#         else:
#             layer_size = 0
#
#         for _ in range(layer_size):
#             current = queue.pop(0)
#             if current in visited:
#                 continue
#
#             visited.add(current)
#             layers[layer].append(current)
#             if current in adj_list.keys():
#                 queue = queue + list(adj_list[current])
#
#         layer += 1
#
#     return layers


def demo_model():
    global SPEED
    # input("Enter the model's name contained in the Models directory: ")
    model_name = "winner.pkl"

    # Initializing pygame
    pygame.init()

    # Initialise game window
    pygame.display.set_caption('Snakes')
    game_window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    # FPS (frames per second) controller
    fps = pygame.time.Clock()

    # creating snake game
    snake_game = SnakeGame(15, 15)
    drawn_game = drawnGame(snake_game, game_window, (10,10), 780, 780)

    # opening model
    with open(f"./Models/{model_name}", "rb") as file:
        genome: neat.genome.DefaultGenome = pickle.load(file)

    # creating network from genome
    config_path = os.path.join(os.path.dirname(__file__), "config_feedforward.txt")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    net = neat.nn.FeedForwardNetwork.create(genome, config)

    #print(get_model_layers(genome, config))

    # main loop
    running = True
    while running:
        game_window.fill(pygame.Color(0,0,0))

        # Frame Per Second /Refresh Rate
        fps.tick(SPEED)

        snake_game.step()

        # activating network
        output = net.activate(tuple(snake_game.snake.get_state(snake_game.fruit, snake_game.x_tiles, snake_game.y_tiles)))

        # applying direction
        max_out = -1
        max_dir = -1
        for i,n in enumerate(output):
            if n > max_out:
                max_out = n
                max_dir = i
        if max_dir == 0:
            snake_game.moveRight()
        elif max_dir == 1:
            snake_game.moveDown()
        elif max_dir == 2:
            snake_game.moveLeft()
        elif max_dir == 3:
            snake_game.moveUp()

        drawn_game.draw()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    SPEED *= 2
                if event.key == pygame.K_LEFT:
                    if SPEED > 1:
                        SPEED /= 2
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        # Refresh game screen
        pygame.display.update()

demo_model()