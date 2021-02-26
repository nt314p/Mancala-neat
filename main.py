#    *5 *4 *3 *2 *1 *0 
#    12 11 10  9  8  7 
#  13                  6
#     0  1  2  3  4  5
#    *0 *1 *2 *3 *4 *5
class Player:
    score = 0

    def takeTurn(self, board): # should return a number from 0 to 5 indicating the pocket
        printBoard(board)
        return int(input("Move (0-5): "))

    def setScore(self, score):
        self.score = score


def game(p1, p2):
    print("Starting game...")
    board = [5, 0, 0, 0, 0, 0, 10, 9, 0, 0, 0, 0, 0, 10]
    isP1Turn = True

    for i in range(14):
        board.append(4 if i % 7 != 6 else 0)

    while True:
        print("Player " + ("1" if isP1Turn else "2") + "'s turn")
        if isP1Turn:
            move = p1.takeTurn(board)
        else:
            move = p2.takeTurn(board)
            move += 7

        stones = board[move]
        board[move] = 0
        index = (move + 1) % 14

        anotherTurn = False

        while stones > 0:
            if index % 7 == 6: # index is currently looking at a store
                if index == (13 if isP1Turn else 6): # index at opponent's store
                    index = (index + 1) % 14
                    continue # skip over
                elif stones == 1: # on your own store and its your last stone
                    board[index] += 1
                    anotherTurn = True
                    break
            
            board[index] += 1

            isOnSide = (index < 6) if isP1Turn else (6 < index and index < 13)

            if stones == 1 and board[index] == 1 and isOnSide: # on your last stone and you placed in an empty pocket
                if board[12 - index] > 0: # if the pocket across from isn't empty
                    sum = board[index] + board[12 - index]
                    board[index] = 0
                    board[12 - index] = 0
                    board[6 if isP1Turn else 13] += sum

            index = (index + 1) % 14
            stones -= 1
        
        # empty check
        sumP1 = 0
        for i in range(0, 6):
            sumP1 += board[i]

        sumP2 = 0
        for i in range(7, 13):
            sumP2 += board[i]

        if sumP1 == 0:
            board[13] += sumP2
            break

        if sumP2 == 0:
            board[6] += sumP1
            break

        if not anotherTurn:
            isP1Turn = not isP1Turn
        else:
            print("Player " + ("1" if isP1Turn else "2") + " goes again")
    
    print("Game Over!")
    print("Player 1: " + str(board[6]))
    print("Player 2: " + str(board[13]))
    printBoard(board)

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

p1 = Player()
p2 = Player()

game(p1, p2)