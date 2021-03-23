import board
import random
from itertools import combinations

query_directions = board.query_directions


# for grouping
def intersect_bombs(intersect):
    for cell in intersect:
        if cell.is_bomb:
            return True
        else:
            return False


# for grouping
def has_common_neighbors(cell0, cell1):
    neighbors_set0 = set()
    for neighbor in cell0.hiddden_neighbors:
        neighbors_set0.add(neighbor)

    neighbors_set1 = set()
    for neighbor in cell1.hidden_neighbors:
        neighbors_set1.add(neighbor)

    intersect = neighbors_set0.intersection(neighbors_set1)
    intersect = filter(intersect_bombs(), intersect)

    return len(intersect) > 0


class Agent:
    class Cell:
        # Creates info about a Cell to be stored in the Agent's knowledge base
        def __init__(self, is_bomb, neighbors, safe_neighbors, bomb_neighbors, hidden_neighbors, clue=None):
            self.is_bomb = is_bomb
            self.neighbors = neighbors
            self.safe_neighbors = safe_neighbors  # Revealed safe neighbors
            self.bomb_neighbors = bomb_neighbors  # Revealed bomb neighbors
            self.hidden_neighbors = hidden_neighbors  # Neighbors not revealed
            self.clue = clue  # None when not queried, -1 when bomb
            return

    # Creates an Agent instance
    def __init__(self, board, stop_on_bomb=False):
        self.board = board
        self.data = {}  # Knowledge base to be populated by cells
        self.fringe = []  # Remaining cells to check
        self.stop_on_bomb = stop_on_bomb  # Stop stepping when a bomb is hit
        self.hit = 0  # Count for bombs hit or if stop_on_bomb=True, the position of the bomb

        # By default, everything is hidden and not a bomb
        for y in range(0, self.board.d):
            for x in range(0, self.board.d):
                pos = (y, x)
                neighbors = self.board.get_neighbors(pos)

                self.data[pos] = Agent.Cell(
                    is_bomb=False,
                    neighbors=neighbors,
                    safe_neighbors=[],
                    bomb_neighbors=[],
                    hidden_neighbors=neighbors.copy()
                )
                self.fringe.append(pos)
        return

    # Runs the Basic Agent
    def run(self):
        try:
            while len(self.fringe) > 0:
                index = random.randrange(0, len(self.fringe), 1)
                pos = self.fringe[index]
                self.step(pos)
        except:  # Loop will end if stop_on_bomb is True and a bomb is hit
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

        if (clue == -1):  # If cell is a bomb, mark as a bomb and pop out a recurse
            self.mark_bomb(pos)
            if (self.stop_on_bomb):  # If we need to stop when we hit a bomb, throw an exception
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
            if neighbor_pos in self.fringe:  # If not queried yet, query
                self.step(neighbor_pos)
            else:  # Else, just check if surrounded by safe or not
                self.check_neighbors(neighbor_pos)
        return

    # Checks if the cell is surrounded by either bombs or safe tiles
    def check_neighbors(self, pos):
        cell = self.data[pos]
        if cell.clue == None:  # Ignore cells that don't have enough info to check neighbors
            return

        if self.is_surrounded_by_bombs(pos):  # If a cell is surrounded by bombs, mark all as bombs
            hidden_neighbors = cell.hidden_neighbors.copy()
            for neighbor_pos in hidden_neighbors:
                self.mark_bomb(neighbor_pos)
                self.remove_from_fringe(neighbor_pos)
        elif self.is_surrounded_by_safe(pos):  # If a cell is surrounded by safe, mark all as safe
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

    # --- Logic Jazz ---
    class lvar:
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return self.name

        def is_lvar(self, var):
            l = self.lvar()
            if type(l) == type(var):
                return True
            else:
                return False

    # runs the Improved Agent
    def run_improve(self):
        groups = self.grouping()

        # queries each group
        for group in groups:
            hidden_logic_vars = {}
            rule_args = []

            for cell in group:
                bomb_count = 0
                hidden_neighbor_logic_vars = []

                for neighbor in cell.neighbors:
                    if neighbor.is_bomb:
                        bomb_count += 1
                        continue

                    if neighbor in cell.hidden_neighbors:
                        hidden_logic_var = None
                        if neighbor in hidden_logic_vars:
                            hidden_logic_var = hidden_logic_vars[neighbor]
                        else:
                            hidden_logic_var = self.lvar(neighbor)
                            hidden_logic_vars[neighbor] = hidden_logic_var

                        hidden_neighbor_logic_vars.append(hidden_logic_var)

                # find all the combinations of where bombs can be
                combs = combinations(hidden_neighbor_logic_vars, cell.clue-bomb_count)

                or_args = []
                for comb in combs:
                    and_args = []
                    for (bomb, index) in comb:
                        and_args.append(hidden_neighbor_logic_vars[index] == bomb)
                        or_args.append(None and and_args)

                rule_args.append(None or or_args)

        rule = None and rule_args

        hidden_lvar_array = []
        for lvar in hidden_logic_vars:
            hidden_lvar_array.append(lvar)

        # what needs to happen:
        #   run probabilities for where bombs are based on hidden cells and the surrounding clues
        #   use each of the probabilities found to determine if there is enough chance of there being a bomb at a given cell
        #   mark bombs and query safe cells (probability of a mine is low enough/confirmed safe)
        # this repeats for each group until all groups are queries aka the board is solved


    # --- Groups cells based on clues that affect them ---
    # by grouping the cells logic can be applied more easily on the location of bombs
    def grouping(self):
        groups = set()
        registered_cell_set = set()

        for y in range(0, self.board.d):
            for x in range(0, self.board.d):
                pos = (y, x)
                cell = self.data[pos]

                group = set()
                self.grouping_starting_from(cell, group, registered_cell_set)

                if len(group) > 0:
                    groups.add(group)

        return groups

    # forms groups from a starting cell
    # includes cells that are still hidden and affected by clues other neighboring cells are affected by
    def grouping_starting_from(self, cell, group, reg_cells, prev_cell):
        if cell in self.finge:      # shouldn't be a part of the group
            return

        if cell.clue == 0:          # ^
            return

        if cell in reg_cells:       # ^
            return

        if cell.bomb_neighbors == cell.clue:
            return

        if not has_common_neighbors(cell, prev_cell):
            return

        group.add(cell)
        reg_cells.add(cell)

        for neighbor in cell.neighbors:
            self.grouping_starting_from(neighbor, group, reg_cells, cell)

        return

# Example usage of improved_agent.py
"""
b = board.Board(20, 60)
b.output()

agent = Agent(b, stop_on_bomb = True)
agent.run_improve()

print("Result:")
print(agent)
"""