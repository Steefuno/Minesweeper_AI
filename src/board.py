import numpy
import random

query_directions = [
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
]

class Board:
    # Creates a Board instance
    def __init__(self, d, n):
        assert (d > 0), "Width must be a positive integer"
        assert (n > 0), "Number of bombs must be a postiive integer"
        self.d = d
        self.board_data = numpy.zeros((d, d), dtype = int)
        self.set_bombs(n)
        return
    
    # Clears the board and randomly places bombs
    def set_bombs(self, n):
        assert (n > 0), "Number of bombs must be a postitive integer"
        assert (n <= self.d ** 2), "Number of bombs must be less than or equal to the number of cells"
        self.board_data.fill(0)

        while (n > 0):
            # Selects a random position
            pos = (random.randint(0, self.d - 1), random.randint(0, self.d - 1))
            # If available, places a bomb
            if (self.board_data[pos[0]][pos[1]] == 0):
                n -= 1
                self.board_data[pos[0]][pos[1]] = 1
        return

    # Queries a cell, returns -1 if tile is a bomb, otherwise returns how many neighboring bombs exist
    def query(self, pos):
        # If queried tile is a bomb, return -1
        if (self.board_data[pos[0]][pos[1]] == 1):
            return -1

        # Counts neighboring bombs
        count = 0
        for direction in query_directions:
            offset_pos = (
                pos[0] + direction[0],
                pos[1] + direction[1]
            )
            if (offset_pos[0] >= self.d) or (offset_pos[0] < 0):
                continue
            if (offset_pos[1] >= self.d) or (offset_pos[1] < 0):
                continue
            count += self.board_data[offset_pos[0]][offset_pos[1]]
        return count
    
    # Get the neighbors of a position
    def get_neighbors(self, pos):
        neighbors = []
        for direction in query_directions:
            offset_pos = (
                pos[0] + direction[0],
                pos[1] + direction[1]
            )
            if (offset_pos[0] < 0) or (offset_pos[0] >= self.d):
                continue
            if (offset_pos[1] < 0) or (offset_pos[1] >= self.d):
                continue
            neighbors.append(offset_pos)
        return neighbors

    # Outputs all the cells of the board
    def output(self):
        for row in self.board_data:
            print(row)
        return

# Example usage of board.py
"""
board = Board(10, 30)
board.output()
print( board.query((5, 5)) )
"""