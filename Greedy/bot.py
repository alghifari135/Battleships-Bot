import argparse
import json
import os
from random import choice

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
map_size = 0
visited_map = [[0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0]]
undef = 99

def main(player_key):
    global map_size
    global visited_map
    global undef
    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)
    map_size = state['MapDimension']
    if state['Phase'] == 1:
        place_ships()
    else:
        opponent_map = state['OpponentMap']['Cells']
        for cell in opponent_map:
            # visited_map[cell['X']][cell['Y']]==0
            if (cell['Damaged']):
                x,y = is_sunk(cell['X'], cell['Y'], state)
                if (is_on_map(x,y,map_size)):
                    output_shot(x,y)
                    return
                # visited_map[cell['X']][cell['Y']]=1
        hunting(opponent_map)

def is_on_map(x,y,map_size):
    return (x>=0 and x<map_size and y>=0 and y<map_size)

def is_sunk(x,y,state):
    global undef
    opponent_map = state['OpponentMap']['Cells']
    map_size = state['MapDimension']
    for cell1 in opponent_map:
        if (cell1['X']==x+1 and cell1['Y']==y):
            break
    for cell2 in opponent_map:
        if (cell2['X']==x-1 and cell2['Y']==y):
            break
    for cell3 in opponent_map:
        if (cell3['X']==x and cell1['Y']==y+1):
            break
    for cell4 in opponent_map:
        if (cell4['X']==x and cell2['Y']==y-1):
            break
    if (cell1['Damaged'] or cell2['Damaged']):
        i, j = check_horizontal(x, y, opponent_map, map_size)
        if (is_on_map(i,j,map_size)):
            return i,j
    elif (cell3['Damaged'] or cell4['Damaged']):
        i, j = check_vertical(x,y,opponent_map, map_size)
        if (is_on_map(i,j,map_size)):
            return i,j
    else:
        i, j = check_vertical(x,y,opponent_map, map_size)
        if (is_on_map(i,j,map_size)):
            return i,j
        else:
            i, j = check_horizontal(x, y, opponent_map, map_size)
            if (is_on_map(i,j,map_size)):
                return i,j
    return undef,undef


def check_vertical(x, y, opponent_map, map_size):
    global undef
    j = y-1
    fail_top = False
    while (is_on_map(x, j, map_size) and not (fail_top)):
        for cell in opponent_map:
            if (cell['X']==x and cell['Y']==j):
                break
        if (cell['Missed']):
            fail_top = True
        elif not (cell['Damaged']):
            return (x,j)
        else:
            j -= 1
    if not (is_on_map(x, j, map_size)):
        fail_top=True    
    j = y+1
    fail_bottom = False
    while (is_on_map(x, j, map_size) and not (fail_bottom)):
        for cell in opponent_map:
            if (cell['X']==x and cell['Y']==j):
                break
        if (cell['Missed']):
            fail_bottom = True
        elif not (cell['Damaged']):
            return (x,j)
        else:
            j += 1
    if not (is_on_map(x, j, map_size)):
        fail_bottom=True
    if (fail_top and fail_bottom):
        return undef,undef

def check_horizontal(x, y, opponent_map, map_size):
    global undef
    i = x+1
    fail_right = False
    while (is_on_map(i, y, map_size) and not fail_right):
        for cell in opponent_map:
            if (cell['X']==i and cell['Y']==y):
                break
        if (cell['Missed']):
            fail_right = True
        elif not (cell['Damaged']):
            return (i,y)
        else:
            i += 1
    if not (is_on_map(i, y, map_size)):
        fail_right=True
    i=x+1
    fail_left = False
    while (is_on_map(i, y, map_size) and not fail_left):
        for cell in opponent_map:
            if (cell['X']==i and cell['Y']==y):
                break
        if (cell['Missed']):
            fail_left = True
        elif not (cell['Damaged']):
            return (i,y)
        else:
            i -= 1
    if not (is_on_map(i, y, map_size)):
        fail_left=True
    if (fail_right and fail_left):
        return undef,undef



def hunting(opponent_map):
	# Search all points that meet these requirements:
	# Have NOT been (damaged OR missed) AND (x+y%2=1)
	targets = []
	for cell in opponent_map:
		oddity = (cell['X']+cell['Y']) % 2
		if not (cell['Damaged'] or cell['Missed']) and oddity:
			valid_cell = cell['X'], cell['Y']
			targets.append(valid_cell)
	target = choice(targets)
	output_shot(*target)
	return

def output_shot(x, y):
    move = 1  # 1=fire shot command code
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass

def place_ships():
	# Please place your ships in the following format <Shipname> <x> <y> <direction>
	# Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
	# Directions: north east south west

    ships = ['Battleship 1 3 north',
             'Carrier 3 0 East',
             'Cruiser 6 1 north',
             'Destroyer 7 7 north',
             'Submarine 4 8 East'
             ]

    with open(os.path.join(output_path, place_ship_file), 'w') as f_out:
        for ship in ships:
            f_out.write(ship)
            f_out.write('\n')
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PlayerKey', nargs='?',
                        help='Player key registered in the game')
    parser.add_argument('WorkingDirectory', nargs='?', default=os.getcwd(
    ), help='Directory for the current game files')
    args = parser.parse_args()
    assert (os.path.isdir(args.WorkingDirectory))
    output_path = args.WorkingDirectory
    main(args.PlayerKey)
