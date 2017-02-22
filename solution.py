assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values
    
    
def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    
    _, unitlist, _, _ = get_layout()
    for unit in unitlist:
        # find all number that consist of 2 digits
        ddigits = [values[box] for box in unit if len(values[box])==2]
        # see if the number occurs more than once in unit
        twindigits = list(set([x for x in ddigits if ddigits.count(x) > 1]))
        if twindigits:
            # remove digits from peers
            for digit in twindigits:
                for box in unit:
                    if (values[box] != digit):
                        assign_value(values, box, values[box].replace(digit[0],'').replace(digit[1],''))
    return values
    
def get_layout():
    """Return list of boxes and knowledge about the relationship between boxes:
    Returns:
        boxes: list of all boxes
        unitlist: list of all units
        units: dict containing all units for all boxes
        peers: dict containing all peers for all boxes
    """
    # Calculate units
    rows = 'ABCDEFGHI'
    cols = '123456789'

    boxes = cross(rows, cols)

    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
    
    # Calculate elements in diagonal units
    diag_units = [cross(r,c) for r,c in zip(rows,cols)]
    diag_units = [item for sublist in diag_units for item in sublist]
    diag_units2 = [cross(r,c) for r,c in zip(rows,cols[::-1])]
    diag_units2 = [item for sublist in diag_units2 for item in sublist]
    diag_units = [diag_units, diag_units2]
    
    unitlist = row_units + column_units + square_units + diag_units
    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
    
    return boxes, unitlist, units, peers
    
def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    
    boxes, _, _, _ = get_layout()
    
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    
    rows = 'ABCDEFGHI'
    cols = '123456789'
    boxes, _, _, _ = get_layout()
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    
    _, _, _, peers = get_layout()
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
            if len(values[peer])==0: return False
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    
    _, unitlist, _, _ = get_layout()
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
            elif len(dplaces)==0:
                return False
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    
    boxes, _, _, _ = get_layout()
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # constrain the search space by identifying naked twins
    values = naked_twins(values)
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus
    for value in values[s]:
        new_sudoku = values.copy()
        assign_value(new_sudoku, s, value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt
        

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    
    values = grid_values(grid)
    
    # run the depth-first search on the sudoku
    values = search(values)
    
    # return solution if search was successful
    return values

if __name__ == '__main__':
    import time
    n = 0
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    
    # Solve the sudoku
    solved = solve(diag_sudoku_grid)
    if solved and n!= 0: 
        display(solved)
        t0 = time.clock()
        for i in range(n):
            solve(diag_sudoku_grid)
        print(time.clock() - t0, "seconds to solve the Sudoku %i times"%n)
    elif not solved:
        print('Failed to solve the Sudoku!')

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
