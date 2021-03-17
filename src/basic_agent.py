import board
import random

query_directions = board.query_directions

class Agent:
    class Cell:
        # Creates info about a Cell to be stored in the Agent's knowledge base
        def __init__(self, is_bomb, neighbors, safe_neighbors, bomb_neighbors, hidden_neighbors, clue = None):
            self.is_bomb = is_bomb
            self.neighbors = neighbors
            self.safe_neighbors = safe_neighbors # Revealed safe neighbors
            self.bomb_neighbors = bomb_neighbors # Revealed bomb neighbors
            self.hidden_neighbors = hidden_neighbors # Neighbors not revealed
            self.clue = clue # None when not queried, -1 when bomb
            return

    # Creates an Agent instance
    def __init__(self, board, stop_on_bomb=False):
        self.board = board
        self.data = {} # Knowledge base to be populated by cells
        self.fringe = [] # Remaining cells to check
        self.stop_on_bomb = stop_on_bomb # Stop stepping when a bomb is hit
        self.hit = 0 # Count for bombs hit or if stop_on_bomb=True, the position of the bomb

        # By default, everything is hidden and not a bomb
        for y in range(0, self.board.d):
            for x in range(0, self.board.d):
                pos = (y, x)
                neighbors = self.board.get_neighbors(pos)

                self.data[pos] = Agent.Cell(
                    is_bomb = False,
                    neighbors = neighbors,
                    safe_neighbors = [],
                    bomb_neighbors = [],
                    hidden_neighbors = neighbors.copy()
                )
                self.fringe.append(pos)
        return
    
    # Runs the Agent
    def run(self):
        try:
            while (len(self.fringe) > 0):
                index = random.randrange(0, len(self.fringe), 1)
                pos = self.fringe[index]
                self.step(pos)
        except: # Loop will end if stop_on_bomb is True and a bomb is hit
            pass
        return

    # Outputs the current information
    def __str__(self):
        s = ""
        for y in range(self.board.d):
            for x in range(self.board.d):
                pos = (y, x)
                cell = self.data[pos]

                cell_output = None
                if (cell.is_bomb):
                    if (self.stop_on_bomb) and (self.hit == pos):
                        cell_output = "E"
                    else:
                        cell_output = "B"
                elif (cell.clue == None):
                    cell_output = "_"
                else:
                    cell_output = cell.clue

                s += "{} ".format(cell_output)
            s += "\n"
        return s

    # Queries a cell, gets data, and recurses through the safe neighbors
    def step(self, pos):
        cell = self.data[pos]
        clue = self.board.query(pos)
        cell.clue = clue

        self.remove_from_fringe(pos)

        if (clue == -1): # If cell is a bomb, mark as a bomb and pop out a recurse
            self.mark_bomb(pos)
            if (self.stop_on_bomb): # If we need to stop when we hit a bomb, throw an exception
                self.hit = pos
                raise Exception()
            else:
                self.hit += 1
                # Check if any neighbors are surrounded by hidden safe cells now that they have one revealed bomb
                hidden_neighbors = cell.hidden_neighbors.copy()
                for neighbor_pos in hidden_neighbors:
                    self.check_neighbors(neighbor_pos)
            return
        # If cell is not a bomb, mark as safe
        self.mark_safe(pos)

        # Checks if hidden neighbors are either all bombs or all safe
        safe_neighbors = cell.safe_neighbors.copy()
        self.check_neighbors(pos)

        # Recurse into neighbors that are deemed safe
        safe_neighbors = cell.safe_neighbors.copy()
        for neighbor_pos in safe_neighbors:
            if (neighbor_pos in self.fringe): # If not queried yet, query
                self.step(neighbor_pos)
            else: # Else, just check if surrounded by safe or not
                self.check_neighbors(neighbor_pos)
        return
        
    # Checks if the cell is surrounded by either bombs or safe tiles
    def check_neighbors(self, pos):
        cell = self.data[pos]
        if (cell.clue == None): # Ignore cells that don't have enough info to check neighbors
            return

        if (self.is_surrounded_by_bombs(pos)): # If a cell is surrounded by bombs, mark all as bombs
            hidden_neighbors = cell.hidden_neighbors.copy()
            for neighbor_pos in hidden_neighbors:
                self.mark_bomb(neighbor_pos)
                self.remove_from_fringe(neighbor_pos)
        elif (self.is_surrounded_by_safe(pos)): # If a cell is surrounded by safe, mark all as safe
            hidden_neighbors = cell.hidden_neighbors.copy()
            for neighbor_pos in hidden_neighbors:
                self.mark_safe(neighbor_pos)

                # Checks neighbors of the newly marked neighbors
                self.check_neighbors(neighbor_pos)
        return

    # Removes a position from the fringe to not get queried later
    def remove_from_fringe(self, pos):
        if not (pos in self.fringe):
            return
        for (index, position) in enumerate(self.fringe):
            if (pos == position):
                self.fringe.pop(index)
                break
        return

    # Set this cell as a bomb to itself and all of its neighbors
    def mark_bomb(self, pos):
        cell = self.data[pos]
        cell.is_bomb = True
        for neighbor_pos in cell.neighbors:
            neighbor = self.data[neighbor_pos]
            neighbor.bomb_neighbors.append(pos)
        self.mark_visible(pos)
        return

    # Set this cell as safe to all of its neighbors
    def mark_safe(self, pos):
        cell = self.data[pos]
        for neighbor_pos in cell.neighbors:
            neighbor = self.data[neighbor_pos]
            if not (pos in neighbor.safe_neighbors):
                neighbor.safe_neighbors.append(pos)
        self.mark_visible(pos)
        return

    # Removes this cell as hidden to all of its neighbors
    def mark_visible(self, pos):
        cell = self.data[pos]
        for neighbor_pos in cell.neighbors:
            neighbor = self.data[neighbor_pos]
            for (index, neighbor_neighbor_pos) in enumerate(neighbor.hidden_neighbors):
                if (neighbor_neighbor_pos == pos):
                    neighbor.hidden_neighbors.pop(index)
                    break
        return

    # Checks if all hidden neighbors are bombs
    def is_surrounded_by_bombs(self, pos):
        cell = self.data[pos]
        hidden_bomb_neighbors_n = cell.clue - len(cell.bomb_neighbors)
        hidden_neighbors_n = len(cell.hidden_neighbors)

        return (hidden_neighbors_n == hidden_bomb_neighbors_n) and (hidden_neighbors_n > 0)


    # Checks if all hidden neighbors are safe
    def is_surrounded_by_safe(self, pos):
        cell = self.data[pos]
        hidden_safe_neighbors = len(cell.neighbors) - cell.clue - len(cell.safe_neighbors)
        hidden_neighbors_n = len(cell.hidden_neighbors)

        return (hidden_neighbors_n == hidden_safe_neighbors) and (hidden_neighbors_n > 0)

# Example usage of basic_agent.py
"""
b = board.Board(20, 60)
b.output()

agent = Agent(b, stop_on_bomb = True)
agent.run()

print("Result:")
print(agent)
"""