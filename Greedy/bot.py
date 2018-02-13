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
        player_own = state['PlayerMap']['Owner']
        for cell in opponent_map:
            # visited_map[cell['X']][cell['Y']]==0
            if (cell['Damaged']):
                x,y = is_sunk(cell['X'], cell['Y'], state)
                if (is_on_map(x,y,map_size)):
                    output_shot(x,y,player_own)
                    return
                # visited_map[cell['X']][cell['Y']]=1
        hunting(opponent_map, player_own)

def is_on_map(x,y,map_size):
    return (x>=0 and x<map_size and y>=0 and y<map_size)

def is_sunk(x,y,state):
    global undef
    opponent_map = state['OpponentMap']['Cells']
    map_size = state['MapDimension']
    
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
        idx = x*10+j
        if (opponent_map[idx]['Missed']):
            fail_top = True
        elif not (opponent_map[idx]['Damaged']):
            return (x,j)
        else:
            j -= 1
    if not (is_on_map(x, j, map_size)):
        fail_top=True

    j = y+1
    fail_bottom = False
    while (is_on_map(x, j, map_size) and not (fail_bottom)):
        idx = x*10+j
        if (opponent_map[idx]['Missed']):
            fail_bottom = True
        elif not (opponent_map[idx]['Damaged']):
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
        idx = i*10+y
        if (opponent_map[idx]['Missed']):
            fail_right = True
        elif not (opponent_map[idx]['Damaged']):
            return (i,y)
        else:
            i += 1
    if not (is_on_map(i, y, map_size)):
        fail_right=True

    i=x-1
    fail_left = False
    while (is_on_map(i, y, map_size) and not fail_left):
        idx = i*10+y
        if (opponent_map[idx]['Missed']):
            fail_left = True
        elif not (opponent_map[idx]['Damaged']):
            return (i,y)
        else:
            i -= 1
    if not (is_on_map(i, y, map_size)):
        fail_left=True

    if (fail_right and fail_left):
        return undef,undef



def hunting(opponent_map,player_own):
	# Search all points that meet these requirements:
	# Have NOT been (damaged OR missed) AND (x+y%2=1)
	targets = []
	for cell in opponent_map:
		oddity = (cell['X']+cell['Y']) % 2
		if not (cell['Damaged'] or cell['Missed']) and oddity:
			valid_cell = cell['X'], cell['Y']
			targets.append(valid_cell)
	target = choice(targets)
	output_shot(*target,player_own)
	return

def output_shot(x, y, player_own):
    energy = player_own['Energy']
    ships = player_own['Ships']
    move = 1
    if (energy>=14):
        for ship in ships :
            if (ship['ShipType']=="Battleship" and not ship['Destroyed']):
                move = 6  # Cross Shot Diagonal
            elif (ship['ShipType'] == "Submarine" and not ship['Destroyed']):
                move = 7  # Seeker Missile
    elif (energy>=10):
        for ship in ships:
            if (ship['ShipType'] == "Submarine" and not ship['Destroyed']):
                move = 7  # Seeker Missile

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
