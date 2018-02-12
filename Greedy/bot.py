import argparse
import json
import os
from random import choice

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
map_size = 0

def main(player_key):
    global map_size
    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)
    map_size = state['MapDimension']
    if state['Phase'] == 1:
        place_ships()
    else:
        hunting(state['OpponentMap']['Cells'])

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

	ships = ['Battleship 1 0 north',
			'Carrier 3 1 East',
			'Cruiser 4 2 north',
			'Destroyer 7 3 north',
			'Submarine 1 8 East'
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
