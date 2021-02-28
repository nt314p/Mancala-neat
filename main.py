import os
import neat
import threading
import visualize

#    *5 *4 *3 *2 *1 *0
#    12 11 10  9  8  7
#  13                  6
#     0  1  2  3  4  5
#    *0 *1 *2 *3 *4 *5

POCKET_MAX_STONES = 29

FITNESS_WIN = 100
FITNESS_LOSS = -30
FITNESS_STONES_GAINED_FACTOR = 1
FITNESS_VALID_MOVE = 0.5
FITNESS_INVALID_MOVE = -1000
ELIMINATE_ON_INVALID_MOVE = True

class Player:
    def takeTurn(self, board):  # should return a number from 0 to 5 indicating the pocket
        printBoard(board)
        return int(input("Move (0-5): "))

    def didWin(self, winner):
        print("I " + "won!" if winner else "lost...")

    def gainedStones(self, stones):
        print("Gained " + str(stones) + " stones")

    def invalidMove(self):
        print("Invalid move!")
        return False

    def validMove(self):
        pass


class NetworkPlayer(Player):
    def __init__(self, net, genome):
        self.net = net
        self.genome = genome

    def takeTurn(self, board):
        boardInput = []

        for i in range((POCKET_MAX_STONES + 1) * 12):
            boardInput.append(0)

        index = 0
        for i in range(14):
            if i == 6 or i == 13:
                continue
            
            boardInput[12 * board[i] + index] = 1
            index += 1

        outputs = self.net.activate(boardInput)

        highest = 0
        for i in range(1, len(outputs)):  # highest output is chosen
            if (outputs[i] > outputs[highest]):
                highest = i

        return highest

    def didWin(self, winner):
        self.genome.fitness += FITNESS_WIN if winner else FITNESS_LOSS

    def gainedStones(self, stones):
        self.genome.fitness += stones * FITNESS_STONES_GAINED_FACTOR

    def invalidMove(self):
        self.genome.fitness += FITNESS_INVALID_MOVE
        return True

    def validMove(self):
        self.genome.fitness += FITNESS_VALID_MOVE

def game(p1, p2, verbose=False):
    if verbose:
        print("Starting game...")
    board = []
    isP1Turn = True

    for i in range(14):
        board.append(4 if i % 7 != 6 else 0)

    while True:
        if verbose:
            print("Player " + ("1" if isP1Turn else "2") + "'s turn")
        if isP1Turn:
            move = p1.takeTurn(board)
            while move < 0 or move > 5 or board[move] == 0:
                if p1.invalidMove():
                    return (-1, 0)
                move = p1.takeTurn(board)
        else:
            rotatedBoard = []
            for i in range(14):
                rotatedBoard.append(board[(i + 7) % 14])

            move = p2.takeTurn(rotatedBoard)
            while move < 0 or move > 5 or rotatedBoard[move] == 0:
                if p2.invalidMove():
                    return (0, -1)
                move = p2.takeTurn(rotatedBoard)

            move += 7

        stones = board[move]
        board[move] = 0
        index = (move + 1) % 14

        prevStones = board[6 if isP1Turn else 13]
        anotherTurn = False

        while stones > 0:
            if index % 7 == 6:  # index is currently looking at a store
                if index == (13 if isP1Turn else 6):  # index at opponent's store
                    index = (index + 1) % 14
                    continue  # skip over
                elif stones == 1:  # on your own store and its your last stone
                    anotherTurn = True

            board[index] += 1

            isOnSide = (index < 6) if isP1Turn else (6 < index and index < 13)

            # on your last stone and you placed in an empty pocket
            if stones == 1 and board[index] == 1 and isOnSide:
                if board[12 - index] > 0:  # if the pocket across from isn't empty
                    sum = board[index] + board[12 - index]
                    board[index] = 0
                    board[12 - index] = 0
                    board[6 if isP1Turn else 13] += sum

            index = (index + 1) % 14
            stones -= 1

            # calculate stones gained
            currStones = board[6 if isP1Turn else 13]
            if (currStones > prevStones):
                diff = currStones - prevStones
                (p1 if isP1Turn else p2).gainedStones(diff)
                prevStones = currStones

        # empty check
        sumP1 = 0
        sumP2 = 0

        for i in range(0, 6):
            sumP1 += board[i]

        for i in range(7, 13):
            sumP2 += board[i]

        if sumP1 == 0:
            board[13] += sumP2
            p2.gainedStones(sumP2)
            break

        if sumP2 == 0:
            board[6] += sumP1
            p1.gainedStones(sumP1)
            break

        if not anotherTurn:
            isP1Turn = not isP1Turn
        elif verbose:
            print("Player " + ("1" if isP1Turn else "2") + " goes again")

    if verbose:
        print("Game Over!")
        print("Player 1: " + str(board[6]))
        print("Player 2: " + str(board[13]))
        printBoard(board)

    didP1Win = board[6] >= board[13]
    p1.didWin(didP1Win)
    p1.didWin(didP1Win or board[6] == board[13])  # check for tie

    return (board[6], board[13])


def printBoard(board):
    print("    *5 *4 *3 *2 *1 *0")
    line = "   "
    for i in range(12, 6, -1):
        line += str(board[i]).rjust(3)

    print(line)

    print("  " + str(board[13]).rjust(2) + " "*17 + str(board[6]).rjust(2))

    line = "   "
    for i in range(0, 6):
        line += str(board[i]).rjust(3)

    print(line)
    print("    *0 *1 *2 *3 *4 *5")

# p1 = Player()
# p2 = Player()
# game(p1, p2, True)

def eval_genomes(genomes, config):
    players = []
    successfulGames = 0

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        players.append(NetworkPlayer(net, genome))

    for i in range(len(players)):
        if players[i] is None:
            continue
        for j in range(len(players)):
            if players[i] is None:
                break
            if i == j or players[j] is None:
                continue

            p1, p2 = game(players[i], players[j], False)

            if ELIMINATE_ON_INVALID_MOVE:
                if p1 == -1:
                    players[i] = None
                elif p2 == -1:
                    players[j] = None

            if p1 != -1 and p2 != -1:
                successfulGames += 1

    print(str(successfulGames) + " successful games")

    try:
        best = stats.best_genome()

        global prevBest

        if prevBest is None or prevBest != best:
            print(best)
            # visualize.draw_net(config, best, True)
            prevBest = best

        # visualize.plot_stats(stats, ylog=False, view=True)
        # visualize.plot_species(stats, view=True)
    except:
        pass


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    
    global stats
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    global prevBest
    prevBest = None

    winner = p.run(eval_genomes)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
