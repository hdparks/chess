import numpy as np
import re

# Color definitions
white = 1
black = -1

# Piece Definitions:
pawn = 1
bishop = 2
knight = 3
rook = 4
queen = 5
king = 6

str_val = {
"" : pawn,
"B": bishop,
"N" : knight,
"R" : rook,
"Q" : queen,
"K" : king
}

file_val = { l:i for i,l in enumerate('abcdefgh')}
rank_val = { str(8-i):i for i in range(8)}


# Default board configuration at the start of each game
starting_board = np.array([
    [black * rook, black * knight, black * bishop, black * queen, black * king, black * bishop, black * knight, black * rook],
    [black * pawn ]*8,
    [0]*8,
    [0]*8,
    [0]*8,
    [0]*8,
    [white * pawn]*8,
    [white * rook, white * knight, white * bishop, white * queen, white * king, white * bishop, white * knight, white * rook]
])

moves_re = re.compile('(?:(K|Q|R|B|N)?([a-h])?([1-8])?(x)?([a-h])([1-8])|(O-O-O)|(O-O))[+#]?')

def is_valid(piece,color,before,after,x=False):
    """
    Returns a boolean value : whether a given move is valid or not

    Parameters
    ----------
    piece : int, value determining type of piece
    before : ndarray(2,), current coordinates of piece
    after : ndarray(2,), proposed ending coordinates of piece

    Returns
    -------
    is_valid : bool, validity of move
    """
    d_rank, d_file = after - before
    print(d_rank,d_file)
    # ---- PAWN ----
    if piece is pawn:
        # Non-captures
        if not x:
            if d_file != 0:
                return False

            # Double move forward on first step
            if before[0] == (1 if color == black else 6):
                print("Can double move")
                if d_rank == -2 * color: return True

            # Single move forward
            return d_rank == -1 * color

        # Captures
        else:
            return d_file in (-1,1) and d_rank == -1 * color

    if piece is bishop:
        return abs(d_rank) == abs(d_file)

    if piece is rook:
        return (d_rank == 0 or d_file == 0)

    if piece is queen:
        return d_rank == 0 or d_file == 0 or d_rank == d_file

    if piece is king:
        return d_rank in (-1,0,1) and d_file in (-1,0,1)

    if piece is knight:
        return (d_rank in (-1,1) and d_file in (-2,2)) or (d_file in (-1,1) and d_rank in (-2,2))

    return False

def take_next_steps(board,input,color=white):
    """
    Applies next input step, modifying the board state

    Parameters
    ----------
    board : ndarray(8,8), the current board state
    input : list(string), the action to be taken
    color : int {-1,1}, denotes which player is taking the given action

    Modifies board in place to save space
    """
    print(input)
    print('color:',color)
    # Kingside Castle
    if input[-1]:
        rank = -1 if color is white else 0
        board[rank,7] = 0
        board[rank,4] = 0
        board[rank,5] = color * rook
        board[rank,6] = color * king
        return

    # Queenside Castle
    if input[-2]:
        rank = -1 if color is white else 0
        board[rank,0] = 0
        board[rank,4] = 0
        board[rank,3] = color * rook
        board[randk,2] = color * king
        return

    # Normal move
    piece = str_val[input[0]]
    after = np.array([rank_val[input[5]],file_val[input[4]]])
    befores = np.argwhere(board == piece * color)

    if befores.shape[0] > 1:
        # filter befores
        if input[1]:
            befores = befores[befores[:,1] == file_val[input[1]]]

        if input[2]:
            befores = befores[befores[:,0] == rank_val[input[2]]]

        # Find where it could have moved from
        if len(befores > 1):
            valids  = [is_valid(piece, color, b, after, input[3]=="x") for b in befores]
            befores = befores[valids]

    # Befores is now single value
    print(befores)

    br,bf = befores[0]
    ar,af = after
    board[br,bf] = 0
    board[ar,af] = piece * color
    return



def get_boards(game_string):
    # Start with default board
    board = starting_board.copy()
    boards = []
    color = white

    # Read in moveset
    moves = moves_re.findall(game_string)

    # Recreate game one step at a time
    for move in moves:
        take_next_steps(board,move,color)
        color = black if color is white else white
        boards.append(board.copy())

    return boards

def read_games(filename):
    games = []
    outcomes = []
    next_outcome = -1

    with open(filename,'r') as myfile:
        lines = myfile.readlines()

    for i,line in enumerate(lines):
        if line[:2] == "1.":
            games.append(line)
            next_outcome = i + 2

        if i == next_outcome:
            outcomes.append(line)


    return games, outcomes

def one_hot_boards(boards):
    one_hots = []
    for board in boards:
        one_hot = np.zeros((64,13),dtype=bool)
        one_hot[np.arange(64),(board+6).flatten()] = True
        one_hot = np.delete(one_hot,6,axis=1)
        one_hots.append(one_hot.flatten())
    return one_hots

def inflate_boards(one_hots):
    boards = []
    for one_hot in one_hots:
        board = np.argmax(one_hot.reshape(64,-1),axis=0) - 6
        boards.append(board.reshape(8,8))

    return boards
